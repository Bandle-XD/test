import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 数据读取--------------

f = open("D:/Project/数据分析/项目一信用卡检测/creditcard.csv")
data = pd.read_csv(f)
f.close()


# 数据标准化处理------------

# 这里fit_transform方法里必须是二维numpy数组，所以要reshape，reshape(-1, 1)的意思是
# 在不知道具体维度的情况下，生成一列，行数由计算机去计算
from sklearn.preprocessing import StandardScaler
data['normAmount'] = StandardScaler().fit_transform(data['Amount'].values.reshape(-1, 1)) 
data = data.drop(['Time','Amount'],axis=1)  # 去掉没用的列，drop默认删除行，axis=1删除列


# 下采样方案-------------------------

# 由于Class里面异常数据远小于正常数据，机器学习会学的“不均衡”，所以可以采取两种方法
# 过采样和下采样，这里采用下采样，即从海量正常数据里面选取和异常数据量相同数量的正常数据
X = data.iloc[:, data.columns != 'Class'] # 特征
y = data.iloc[:, data.columns == 'Class'] # 样本值

# 得到所有异常样本的索引
number_records_fraud = len(data[data.Class == 1]) # data.Class == 1是bool索引，得到异常样本的数量
fraud_indices = np.array(data[data.Class == 1].index) # 异常样本索引

# 得到所有正常样本的索引
normal_indices = data[data.Class == 0].index

# 在正常样本中随机采样出指定个数的样本，并取其索引
random_normal_indices = np.random.choice(normal_indices, number_records_fraud, replace = False) # replace = False是不替换原始数据
random_normal_indices = np.array(random_normal_indices)

# 有了正常和异常样本后把它们的索引都拿到手
under_sample_indices = np.concatenate([fraud_indices,random_normal_indices]) # 拼接得到下采样索引

# 根据索引得到下采样所有样本点
under_sample_data = data.iloc[under_sample_indices,:]

X_undersample = under_sample_data.iloc[:, under_sample_data.columns != 'Class'] # 下采样样本特征
y_undersample = under_sample_data.iloc[:, under_sample_data.columns == 'Class'] # 下采样样本值


# 数据集划分------------------

# 整个数据集进行划分
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 0.3, random_state = 0) # random_state是保证每次随机性相同，类似随机种子

# 下采样数据集进行划分
X_train_undersample, X_test_undersample, y_train_undersample, y_test_undersample = \
train_test_split(X_undersample,y_undersample,test_size = 0.3,random_state = 0)


# 逻辑回归模型------------------

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import confusion_matrix,recall_score,classification_report 
from sklearn.model_selection import cross_val_predict

# 交叉验证函数，对于已经使用train_test_split进行分组的数据集，可直接使用cross_val_score
def printing_Kfold_scores(x_train_data,y_train_data):
    fold = KFold(5,shuffle=False) # 

    # 定义不同力度的正则化惩罚力度
    c_param_range = [0.01,0.1,1,10,100]
    # 展示结果用的表格
    results_table = pd.DataFrame(index = range(len(c_param_range),2), columns = ['C_parameter','Mean recall score'])
    results_table['C_parameter'] = c_param_range

    # k-fold 表示K折的交叉验证，这里会得到两个索引集合: 训练集 = indices[0], 验证集 = indices[1]
    j = 0
    #循环遍历不同的参数
    for c_param in c_param_range:
        print('-------------------------------------------')
        print('正则化惩罚力度: ', c_param)
        print('-------------------------------------------')
        print('')

        recall_accs = []
        
        #一步步分解来执行交叉验证
        for iteration, indices in enumerate(fold.split(x_train_data),start=1):

            # 指定算法模型，并且给定参数
            lr = LogisticRegression(C = c_param, penalty = 'l1',solver = 'liblinear') # penalty是预测方法，分为l1和l2

            # 训练模型，注意索引不要给错了，训练的时候一定传入的是训练集，所以X和Y的索引都是0
            lr.fit(x_train_data.iloc[indices[0],:],y_train_data.iloc[indices[0],:].values.ravel())

            # 建立好模型后，预测模型结果，这里用的就是验证集，索引为1
            y_pred_undersample = lr.predict(x_train_data.iloc[indices[1],:].values)

            # 有了预测结果之后就可以来进行评估了，这里recall_score需要传入预测值和真实值。
            recall_acc = recall_score(y_train_data.iloc[indices[1],:].values,y_pred_undersample)
            # 一会还要算平均，所以把每一步的结果都先保存起来。
            recall_accs.append(recall_acc)
            print('Iteration ', iteration,': 召回率 = ', recall_acc)

        # 当执行完所有的交叉验证后，计算平均结果
        results_table.loc[j,'Mean recall score'] = np.mean(recall_accs)
        j += 1
        print('')
        print('平均召回率 ', np.mean(recall_accs))
        print('')
        
    #找到最好的参数，哪一个Recall高，自然就是最好的了。
    best_c = results_table.loc[results_table['Mean recall score'].astype('float32').idxmax()]['C_parameter']
    
    # 打印最好的结果
    print('*********************************************************************************')
    print('效果最好的模型所选参数 = ', best_c)
    print('*********************************************************************************')
    
    return best_c

best_c = printing_Kfold_scores(X_train_undersample,y_train_undersample)
#####