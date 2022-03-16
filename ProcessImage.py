import cv2
from PIL import Image
import numpy as np
from PIL import ImageEnhance
import csv

class ProcessImage:
    """
    Image Processing
    """
    def __init__(self,img):
        self.img = img
        self.img_SE = []
        self.img_SE_HSV = []
        self.img_SE_HSV_H = []
        self.BIN_SE_HSV_img_H = []

        self.particle_list = []
        self.areas = []
        self.area_image = 0
        self.dias = []
        self.count = 0
        self.range_size = []

        self.total_area = 0
        self.mean_area = 0
        self.std_area = 0
        self.mean_dia = 0
        self.std_dia = 0
        self.ratio_area = 0

    def sharpness_ImageEnhance(self,file):
        '''
        Image enhancement sharpening
        :param file: The path of img file
        :return:
        '''
        img_origin = Image.open(file)
        enh_sha = ImageEnhance.Sharpness(img_origin)
        sharpness = 10
        image_sharped = enh_sha.enhance(sharpness)
        image_sharped = cv2.cvtColor(np.array(image_sharped), cv2.COLOR_RGB2BGR)
        return image_sharped

    def process(self,threshold = 25):
        '''
        binarizer image
        '''
        self.img_SE = self.sharpness_ImageEnhance(self.img)
        self.img_SE = cv2.resize(self.img_SE , (512, 512))
        self.img_SE_HSV = cv2.cvtColor(self.img_SE, cv2.COLOR_BGR2HSV)

        self.img_SE_HSV_H = self.img_SE_HSV[:, :, 0]
        ret, self.BIN_SE_HSV_img_H = cv2.threshold(self.img_SE_HSV_H, threshold, 255, cv2.THRESH_BINARY)


    def evaluate(self,type):
        '''
        Evaluate the result of binarization
        :param type: type of evaluate, 'FN' or 'FP'

        '''
        if type == 'FN':
            mask = self.BIN_SE_HSV_img_H // 255
        elif type == 'FP':
            mask = 1 - self.BIN_SE_HSV_img_H // 255
        else:
            mask = 0
        (B, G, R) = cv2.split(self.img_SE)
        img_evaluate = cv2.merge([B * mask, G * mask, R * mask])
        cv2.imshow('img_'+ type, img_evaluate)


    def extract(self,scaler = 0.24,min_area = 0.5):
        '''
        Extract the particles in the binarized image
        :param scaler: The scale of the image, the default is 0.24 μm/pixel
        :param min_area: Minimum particle area to keep
        '''
        ret, thresh = cv2.threshold(self.BIN_SE_HSV_img_H, 127, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        self.area_image = self.BIN_SE_HSV_img_H.size * scaler * scaler

        for cont in contours:
            raw_data = []
            area = cv2.contourArea(cont) * scaler * scaler
            if area < min_area:
                continue
            self.areas.append(area)
            self.count += 1
            rect = cv2.boundingRect(cont)
            dia_pixel = int((rect[2] + rect[3]) / 2)
            dia = dia_pixel * scaler
            self.dias.append(dia)

            cv2.rectangle(self.img_SE, rect, (0, 0, 255), 2)
            mm = cv2.moments(cont)
            cx = mm['m10'] / mm['m00']
            cy = mm['m01'] / mm['m00']

            raw_data.append(self.count)
            raw_data.append(area)
            raw_data.append(dia)
            raw_data.append([cx, cy])

            self.particle_list.append(raw_data)

        if len(self.particle_list) > 0:
            self.range_size = [min(self.dias), max(self.dias), min(self.areas), max(self.areas)]

    def calculateFeatures(self):
        '''
        Calculate the particle features in the image, including total area, average area, standard deviation of area,
        average diameter, standard deviation of diameter, and the proportion of particles in the total image
        '''
        self.total_area = np.sum(self.areas)
        self.mean_area = np.mean(self.areas)
        self.std_area = np.std(self.areas)
        self.mean_dia = np.mean(self.dias)
        self.std_dia = np.std(self.dias)
        self.ratio_area = self.total_area / self.area_image

    def export(self,file_export):
        '''
        Export the information of the particles in the figure to a csv file
        '''
        with open(file_export, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Total Area', 'Average Area', 'Std of Area', 'Average Diameter', 'Std of Diameter','Ratio of particles'])
            writer.writerow([self.total_area,self.mean_area,self.std_area,self.mean_dia,self.std_dia,self.ratio_area])
            writer.writerow(['No.', 'Area', 'Diameter', 'Location'])
            for raw_data in self.particle_list:
                writer.writerow(raw_data)


if __name__ == "__main__":
    pro = ProcessImage("./Data/751b_x63_zoom08_1.tif")

    pro.process(15)
    pro.evaluate('FN')
    pro.evaluate('FP')
    pro.extract()
    pro.calculateFeatures()
    pro.export('./data/Result.csv')
    cv2.waitKey()




