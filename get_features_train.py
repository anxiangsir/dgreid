import argparse
import os
import pickle

import numpy as np
import torch
from torch import nn
from torch.backends import cudnn
from torch.utils.data import DataLoader

from config import cfg
from data import make_data_loader
from data.datasets.dataset_loader import TestImageDataset
from data.transforms import build_transforms
from modeling import build_model
from utils.logger import setup_logger

TRAIN_ROOT = "/data/xiangan/reid_final/four_fold/train_split4_rematch/all_origin/bounding_box_train"


def test_collate_fn(batch):
    """test data collate function"""
    return torch.stack(batch, dim=0)


def main():
    parser = argparse.ArgumentParser(description="ReID Baseline Training")
    parser.add_argument("--config_file", type=str)
    parser.add_argument("opts", help="Modify config options using the command-line", default=None,
                        nargs=argparse.REMAINDER)

    args = parser.parse_args()

    num_gpus = int(os.environ["WORLD_SIZE"]) if "WORLD_SIZE" in os.environ else 1

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    cfg.freeze()

    output_dir = cfg.OUTPUT_DIR
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logger = setup_logger("reid_baseline", output_dir, 0)
    logger.info("Using {} GPUS".format(num_gpus))
    logger.info(args)

    if args.config_file != "":
        logger.info("Loaded configuration file {}".format(args.config_file))
        with open(args.config_file, 'r') as cf:
            config_str = "\n" + cf.read()
            logger.info(config_str)
    logger.info("Running with config:\n{}".format(cfg))

    if cfg.MODEL.DEVICE == "cuda":
        os.environ['CUDA_VISIBLE_DEVICES'] = cfg.MODEL.DEVICE_ID  # new add by gu
    cudnn.benchmark = True

    _1, _2, _3, num_classes = make_data_loader(cfg)
    model = build_model(cfg, num_classes)
    model.load_param(cfg.TEST.WEIGHT)

    # gpu_device
    device = cfg.MODEL.DEVICE

    if device:
        if torch.cuda.device_count() > 1:
            model = nn.DataParallel(model)
        model.to(device)

    # test data-loader
    test_transforms = build_transforms(cfg, is_train=False)

    img_name = os.listdir(TRAIN_ROOT)

    dataset = [os.path.join(TRAIN_ROOT, x) for x in img_name]
    test_set = TestImageDataset(
        dataset=dataset,
        transform=test_transforms
    )

    test_loader = DataLoader(
        test_set, batch_size=cfg.TEST.IMS_PER_BATCH, shuffle=False,
        num_workers=12, collate_fn=test_collate_fn
    )

    result = []

    # _inference
    def _inference(batch):
        model.eval()
        with torch.no_grad():
            data = batch
            data = data.to(device) if torch.cuda.device_count() >= 1 else data
            feat = model(data)
            feat = feat.data.cpu().numpy()
            return feat

    count = 0
    for batch in test_loader:
        count += 1
        feat = _inference(batch)
        result.append(feat)

        if count % 100 == 0:
            print(count)

    result = np.concatenate(result, axis=0)

    pickle.dump([result, img_name], open(cfg.OUTPUT_DIR + '/train_feature.feat', 'wb'))


if __name__ == '__main__':
    main()