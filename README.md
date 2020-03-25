[English version]() 
comming soon!
### 比赛结果
> 初赛14/466名(去重后的结果)，复赛25/68名;
### 比赛比较重要的一些trick
这些结果都是线下四折交叉验证的结果，我们线下和线上是一致的，线上的得分没有做记录。
#### 1. RandomPatch
`RandomPatch`是一个遮挡类型的数据增强，我们引用了zhou的方法。和RandomErasing类似，也是类似于在图片中随机增加噪音，不过这些噪音不是均值，也不是0，而是随机来自训练集的patch，这可以用一个队列来实现。这个数据增强在本次的比赛中提升很大。
|   randompatch_prob  | split1(mAP/Rank-1) |   split2  |   split3  |   split4  |     avg     |
|:-------------------:|:------------------:|:---------:|:---------:|:---------:|:-----------:|
| (prob=0.10) |      82.9/93.4     | 81.5/92.6 | 80.3/91.4 | 82.7/92.6 | 81.85/92.50 |
| (prob=0.30) |      83.6/93.8     | 82.2/92.3 | 80.9/91.8 | 84.2/93.7 | 82.73/92.90 |
| (prob=0.50) |      84.4/94.5     | 82.4/93.0 | 81.6/92.4 | 85.1/94.6 | 83.45/93.63 |
#### 2. 增大图片的分辨率
和检测、分割、分类类似、直接增大图片的分辨率也是会提升性能的。
#### 3. 方差反转
这是一个观察训练集的trick，在初赛的时候，线下的mAP有一个多点的提升。
#### 4. 测试集的利用
比赛是允许使用测试集加入训练集进行训练的，我们使用了一个简单的策略利用测试集
1. 先训练一个base模型，用base模型去提取测试集中query和gallery的特征。
2. 这里做了一个很重要的假设、假设测试集中query每张图片都是独立的id(实际上我们用了层次聚类的方法先对query去重)，让每个**干净**的query，去gallery中搜索，将得分高于阈值的图片与query关联。
3. 将步骤2的图片加入到训练集中，重新训练新的final模型。
4. 以上步骤可以迭代，我们比赛的时候仅做了一次，在初赛和复赛中均有2个点的提升。  
 
#### 5. 复赛测试集domain问题
待续
#### 6. 修改网络结构
基于MGN我们做了一些修改、在8个特征cat成为最终的表征特征时、我们对这个特征加入了centerloss作为监督、centerloss的两个参数做了调参。
| center loss weight | split1(mAP/Rank-1) |   split2  |   split3  |   split4  |     avg     | result |
|:------------------:|:------------------:|:---------:|:---------:|:---------:|:-----------:|:------:|
|   (cw=1e-4)cw001   |      84.4/94.7     | 82.3/93.1 | 81.8/92.8 | 84.5/93.9 | 83.25/93.63 | better |
|  (cw=5e-4)baseline |      83.6/93.8     | 82.2/92.3 | 80.9/91.8 | 84.2/93.7 | 82.73/92.90 |    -   |


#### 7. 其他
1. Pretrain+分层学习率
2. 过采样、SkipSampler
3. 四折交叉验证的划分方法： 按照id去划分、图片少的不算query、测试集加入gallery当作干扰集
4. 比较小的batchsize会比较好(这点疑问很大、感觉因为模型的原因)
5. 待续
### 比赛的反思
1. 我们尝试的还是太少了，大部分时间用在了训练MGN上面，MGN计算量真的大，占用的显存比较多，导致我们没法训练更大的模型，我们用到了FP16混合精度训练，但还是浪费了不少时间，看到其他团队还尝试了arcface，我们都没有去尝试，复赛的时候就MGN用到底了；
2. 颜色抖动这个我们用了，过佳大佬也提到了(arcface作者)，但是没用对，看到不少团队都有很大的提升；
3. 测试集的利用太粗暴了。
4. 大部分时间用来调参了，期间也思考了一下数据集的问题，比如GB反方差和过采样以及测试集跨Domain，这些方法都有很大的提升。
### 预估训练时间，预测时间
1. 训练时间：44小时；
2. 预测：2小时；  

| 步骤         | 时间/h    |
|------------|---------|
| 训练中间模型     | 12 小时   |
| 推理测试集特征    | 0.23 小时 |
| 无监督聚类      | 0.14 小时 |
| 训练最终模型     | 32 小时   |
| 最终模型提取特征时间 | 0.2 小时  |
| reranking  | 2小时     |
| total      | 47      |

### DockerFile

详情见`./DockerFile`.
1. 我们训练和推理的容器为同一个容器；
2. 项目在容器中的路径为：`/workspace/code`
3. 我们checkpoint都存放在了`/tmp/data/model`路径下；
4. 最终的模型为`/tmp/data/model/model_final/se_resnet50_model_75.pth`;
5. 一键运行脚本`bash run.sh`即可


### 引用
1. 
