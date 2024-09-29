from dataclasses import dataclass
import os
import sys
import cv2
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.metrics import Precision, Recall, BinaryAccuracy
from src.exception import CustomException
from src.logger import logging
import dill
import numpy as np


@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join('artifacts', 'mushroom_model.pkl')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
        self.model = None

    def build_model(self):
        logging.info("Building the CNN model.")
        model = Sequential()
        
        model.add(Conv2D(16, (3, 3), activation='relu', input_shape=(256, 256, 3)))
        model.add(MaxPooling2D())
        model.add(Conv2D(32, (3, 3), activation='relu'))
        model.add(MaxPooling2D())
        model.add(Conv2D(16, (3, 3), activation='relu'))
        model.add(MaxPooling2D())
        model.add(Conv2D(16, (3, 3), activation='relu'))
        model.add(MaxPooling2D())
        model.add(Flatten())
        model.add(Dense(256, activation='relu'))
        model.add(Dense(1, activation='sigmoid')) 
        
        return model
    
    def compile_model(self, model):
        logging.info("Compiling the model.")
        model.compile(optimizer='adam', loss=tf.keras.losses.BinaryCrossentropy(), metrics=['accuracy', Precision(), Recall(), BinaryAccuracy()])
        logging.info('Evaluated the model')
        model.summary(print_fn=logging.info)

    def initiate_model_trainer(self, train, val, test, epochs = 10):
        try:
            model = self.build_model()
            self.compile_model(model)

            logging.info("Starting model training.")
            hist = model.fit(train, validation_data=val, epochs=epochs)

            logging.info("Training history: %s", hist.history)

            save_object(file_path=self.model_trainer_config.trained_model_file_path, obj= model)
            logging.info(f'Model saved to {self.model_trainer_config.trained_model_file_path}')
            

        except Exception as e:
            raise CustomException(e, sys)
        
        def predict(self, imagePath: str):
            if self.model is None:
                raise CustomException("Model not loaded.", sys)
            
            img = cv2.imread(imagePath)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            resized_image = tf.image.resize(img, (256,256))

            yPredict = self.model.predict(np.expand_dims(resized_image/255,0))

            if(yPredict >= 0.5):
                probability = yPredict *100
                return {'Ediblility':'1', 'Probability':probability[0][0]}
            else:
                probability = (1- yPredict)*100
                return {'Ediblility':'0', 'Probability':probability[0][0]}
                

def save_object(file_path, obj):
    try:
        dir_path = os.path.dirname(file_path)

        os.makedirs(dir_path, exist_ok = True)

        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)

    except Exception as e:
        raise CustomException(e, sys)