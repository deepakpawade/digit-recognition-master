import keras   #keras already has the dataset 
from keras.datasets import mnist  #get the minst dataset from the keras library 
from keras.models import Sequential #groups a linear stack of layers into a tf.keras.Model.
from keras.layers import Dense, Dropout, Flatten #
from keras.layers import Conv2D, MaxPooling2D  #perform pooling operations
from keras import backend as K

(x_train, y_train), (x_test, y_test) = mnist.load_data()
print(x_train.shape, y_train.shape)

batch_size = 128
num_classes = 10
epochs = 15

# The MNIST dataset contains 28x28 grayscale images. Reshape the training data into 4-dimensional arrays, with the first dimension representing the number of samples (i.e. x_train.shape[0]), the second and third dimensions representing the height and width of the images (i.e. 28, 28), and the fourth dimension representing the number of channels (i.e. 1, since it's a grayscale image)
x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
input_shape = (28, 28, 1)

y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
#  This line normalizes the training data by dividing each pixel value by 255. 
#  Normalization helps improve the accuracy of the model by scaling the input data.

x_train /= 255
x_test /= 255
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),activation='relu',input_shape=input_shape))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))
model.compile(loss=keras.losses.categorical_crossentropy,optimizer=keras.optimizers.Adadelta(),metrics=['accuracy'])

hist = model.fit(x_train, y_train,batch_size=batch_size,epochs=epochs,verbose=1,validation_data=(x_test, y_test))
print("The model has successfully trained")
model.save('mnist.h5')
print("Saving the model as mnist.h5")
