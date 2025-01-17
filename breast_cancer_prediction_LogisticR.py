import numpy as np 
import seaborn as sns
sns.set(style='whitegrid')
import pandas as pd 
import matplotlib.pyplot as plt
import tensorflow.compat.v1 as tf
from tensorflow import keras
from tensorflow.keras import layers

tf.compat.v1.disable_v2_behavior()

print(tf.__version__)

dataset_path = keras.utils.get_file("breast-cancer-wisconsin.data", "http://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/breast-cancer-wisconsin.data")
print("data file location: " +dataset_path)

column_names = ['Patient_ID','Clump_Thickness','Uniformity_of_CellSize','Uniformity_of_CellShape','Marginal_Adhesion','Single_Epithelial_Cell_Size','Bare_Nuclei','Bland_Chromatin','Normal_Nucleoli','Mitoses','Class']

raw_dataset = pd.read_csv(dataset_path, names=column_names,
                      na_values = "?", comment='\t',
                      sep=",", skipinitialspace=True)

dataset = raw_dataset.copy()
print(dataset.tail())

dataset.isna().sum()
dataset = dataset.dropna()


train_stats = dataset.describe()
train_stats = train_stats.transpose()
print(train_stats)

def norm(x):
  return (x - train_stats['mean']) / train_stats['std']
normed_train_data = norm(dataset)

print(normed_train_data)


dataset.Class = dataset.Class.replace(to_replace=[2, 4], value=[0, 1])

X = dataset.drop(labels=['Patient_ID', 'Class'], axis=1).values
y = dataset.Class.values

seed = 5
np.random.seed(seed)
tf.set_random_seed(seed)

# set replace=False, Avoid double sampling
train_index = np.random.choice(len(X), round(len(X) * 0.8), replace=False)

# diff set
test_index = np.array(list(set(range(len(X))) - set(train_index)))
train_X = X[train_index]
train_y = y[train_index]
test_X = X[test_index]
test_y = y[test_index]

def min_max_normalized(data):
    col_max = np.max(data, axis=0)
    col_min = np.min(data, axis=0)
    return np.divide(data - col_min, col_max - col_min)

train_X = min_max_normalized(train_X)
test_X = min_max_normalized(test_X)

print(test_X)

# Begin building the model framework
# Declare the variables that need to be learned and initialization
# There are 4 features here, A's dimension is (4, 1)
A = tf.Variable(tf.random.normal(shape=[9, 1]))
b = tf.Variable(tf.random.normal(shape=[1, 1]))
init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)


data = tf.placeholder(dtype=tf.float32, shape=[None, 9])
target = tf.placeholder(dtype=tf.float32, shape=[None, 1])

# Declare the model you need to learn
mod = tf.matmul(data, A) + b

# Declare loss function
# Use the sigmoid cross-entropy loss function,
# first doing a sigmoid on the model result and then using the cross-entropy loss function
loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=mod, labels=target))

# Define the learning rate， batch_size etc.
learning_rate = 0.003
batch_size = 30
iter_num = 6000

# Define the optimizer
opt = tf.train.GradientDescentOptimizer(learning_rate)

# Define the goal
goal = opt.minimize(loss)

# Define the accuracy
# The default threshold is 0.5, rounded off directly
prediction = tf.round(tf.sigmoid(mod))
# Bool into float32 type
correct = tf.cast(tf.equal(prediction, target), dtype=tf.float32)
# Average
accuracy = tf.reduce_mean(correct)
# End of the definition of the model framework

# Start training model
# Define the variable that stores the result
loss_trace = []
train_acc = []
test_acc = []

# training model
for epoch in range(iter_num):
    # Generate random batch index
    batch_index = np.random.choice(len(train_X), size=batch_size)
    batch_train_X = train_X[batch_index]
    batch_train_y = np.matrix(train_y[batch_index]).T
    sess.run(goal, feed_dict={data: batch_train_X, target: batch_train_y})
    temp_loss = sess.run(loss, feed_dict={data: batch_train_X, target: batch_train_y})
    # convert into a matrix, and the shape of the placeholder to correspond
    temp_train_acc = sess.run(accuracy, feed_dict={data: train_X, target: np.matrix(train_y).T})
    temp_test_acc = sess.run(accuracy, feed_dict={data: test_X, target: np.matrix(test_y).T})
    # recode the result
    loss_trace.append(temp_loss)
    train_acc.append(temp_train_acc)
    test_acc.append(temp_test_acc)
    # output
    if (epoch + 1) % 300 == 0:
        print('epoch: {:4d} loss: {:5f} train_acc: {:5f} test_acc: {:5f}'.format(epoch + 1, temp_loss,
                                                                          temp_train_acc, temp_test_acc))

# Visualization of the results
# loss function
plt.plot(loss_trace)
plt.title('Cross Entropy Loss')
plt.xlabel('epoch')
plt.ylabel('loss')
plt.show()


# accuracy
plt.plot(train_acc, 'b-', label='train accuracy')
plt.plot(test_acc, 'k-', label='test accuracy')
plt.xlabel('epoch')
plt.ylabel('accuracy')
plt.title('Train and Test Accuracy')
plt.legend(loc='best')
plt.show()