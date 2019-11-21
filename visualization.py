import pickle

import numpy as np
from sklearn import preprocessing
import json

def process_info(info):
    """
    get features and normalizing features.
    Args:
        info:

    Returns:

    """
    feats = []
    imgnames = []
    for i in range(len(info)):
        feats.append(info[i][0].flatten())
        imgnames.append(info[i][1])
    feats = np.array(feats)
    feats = preprocessing.normalize(feats)
    return feats, imgnames


def get_clean_query(query_feats, query_imgnames, threshold):
    # score matrix
    query_sim = np.dot(query_feats, query_feats.T)
    #
    count = 0
    # 0.9 0
    # 0.7 17
    # 0.6 160
    # 0.5 789
    dirty_id_set = set()
    clean_id_set = set()
    for idx, distance_arr in enumerate(query_sim):
        if sum(distance_arr > threshold) > 1:
            count += 1
            dirty_id_set.add(query_imgnames[idx])
        else:
            clean_id_set.add(query_imgnames[idx])

    print('dirty id num is:  ', len(dirty_id_set))
    print('clean id num is:  ', len(clean_id_set))
    # count = 4768
    # for clean_name in tqdm(clean_id_set):
    #     input_path = os.path.join(TEST_QUERY_PATH, clean_name)
    #     output_name = os.path.join(OUTPUT_PATH, "%d_c1_%s" % (count, clean_name))
    #     open(output_name, 'wb').write(open(input_path, 'rb').read())
    #     count += 1
    return clean_id_set


def main():
    dirty_threshold = 0.6
    #
    gallery_info = pickle.load(open('features/046/gallery_a_feature.feat', 'rb'))
    query_info = pickle.load(open('features/046/query_a_feature.feat', 'rb'))

    gallery_feats, gallery_imgnames = process_info(gallery_info)
    query_feats, query_imgnames = process_info(query_info)

    clean_query_id_set = get_clean_query(query_feats, query_imgnames, 0.6)

    f = open('ensemblex7.json', encoding='utf-8')
    content = f.read()
    dic = json.loads(content)
    cleaned_rank_dict = {}
    for query_name in list(dic.keys()):
        print(query_name)
        if query_name in clean_query_id_set:
            origin_ranklist = dic[query_name][:10]
            query_cur_feat = query_feats[query_imgnames.index(query_name)]

            cleaned_ranklist = []
            cleaned_count = 0
            for gallery_name in origin_ranklist:
                rank_cur_feat = gallery_feats[gallery_imgnames.index(gallery_name)]
                score = np.dot(query_cur_feat, rank_cur_feat)
                if score > dirty_threshold:
                    cleaned_ranklist.append(gallery_name)
                    cleaned_count += 1
                else:
                    break
            cleaned_rank_dict[query_name] = cleaned_ranklist
            print(cleaned_count)


    # a = open('ensemblex7.json')
    # print(a.readlines()[0])
    # f = open('ensemblex7.json', encoding='utf-8')
    # content = f.read()
    # dic = json.loads(content)
    # for i in dic.keys():
    #     print(i)
    #     print(dic[i])
    # print(dic[dic.keys()])


def visualization():
    pass


if __name__ == '__main__':
    main()