# -*- coding: utf-8 -*-
import face_recognition
import cv2
from gevent import os
import freetype
import copy


class ChineseTextUtil(object):
    def __init__(self, ttf):
        self._face = freetype.Face(ttf)

    def draw_text(self, image, pos, text, text_size, text_color):
        '''
        使用ttf字体库中的字体设置姓名
        :param image:     用于将text生成在某个image图像上
        :param pos:       画text的位置
        :param text:      unicode编码的text
        :param text_size: 字体大小
        :param text_color:字体颜色
        :return:          返回位图
        '''
        self._face.set_char_size(text_size * 64)
        metrics = self._face.size
        ascender = metrics.ascender / 64.0

        # descender = metrics.descender / 64.0
        # height = metrics.height / 64.0
        # linegap = height - ascender + descender
        ypos = int(ascender)

        if not isinstance(text, unicode):
            text = text.decode('utf-8')
        img = self.string_2_bitmap(image, pos[0], pos[1], text, text_color)
        return img

    def string_2_bitmap(self, img, x_pos, y_pos, text, color):
        '''
        将字符串绘制为图片
        :param x_pos: text绘制的x起始坐标
        :param y_pos: text绘制的y起始坐标
        :param text:  text的unicode编码
        :param color: text的RGB颜色编码
        :return:      返回image位图
        '''
        prev_char = 0
        pen = freetype.Vector()
        pen.x = x_pos << 6  # div 64
        pen.y = y_pos << 6

        hscale = 1.0
        matrix = freetype.Matrix(int(hscale) * 0x10000L, int(0.2 * 0x10000L), int(0.0 * 0x10000L), int(1.1 * 0x10000L))
        cur_pen = freetype.Vector()
        pen_translate = freetype.Vector()

        image = copy.deepcopy(img)
        for cur_char in text:
            self._face.set_transform(matrix, pen_translate)

            self._face.load_char(cur_char)
            kerning = self._face.get_kerning(prev_char, cur_char)
            pen.x += kerning.x
            slot = self._face.glyph
            bitmap = slot.bitmap

            cur_pen.x = pen.x
            cur_pen.y = pen.y - slot.bitmap_top * 64
            self.draw_ft_bitmap(image, bitmap, cur_pen, color)

            pen.x += slot.advance.x
            prev_char = cur_char

        return image

    def draw_ft_bitmap(self, img, bitmap, pen, color):
        '''
        draw each char
        :param bitmap: 位图
        :param pen:    画笔
        :param color:  画笔颜色
        :return:       返回加工后的位图
        '''
        x_pos = pen.x >> 6
        y_pos = pen.y >> 6
        cols = bitmap.width
        rows = bitmap.rows

        glyph_pixels = bitmap.buffer

        for row in range(rows):
            for col in range(cols):
                if glyph_pixels[row * cols + col] != 0:
                    img[y_pos + row][x_pos + col][0] = color[0]
                    img[y_pos + row][x_pos + col][1] = color[1]
                    img[y_pos + row][x_pos + col][2] = color[2]


if __name__ == '__main__':
    # 读取图片识别样例
    face_file_list = []
    names_list = []
    face_encoding_list = []

    rootdir = '/Users/z/Desktop/group_face1/'
    list = os.listdir(rootdir)
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isfile(path) and ".jpg" in list[i]:
            face_file_list.append(rootdir + list[i])
            print(list[i][:-4])
            names_list.append(list[i][:-4])

    for path in face_file_list:
        print(path)
        face_image = face_recognition.load_image_file(path)
        face_encoding = face_recognition.face_encodings(face_image)[0]
        face_encoding_list.append(face_encoding)

    # 初始化一些变量用于，面部位置，编码，姓名等
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    video_capture = cv2.VideoCapture(0)
    while True:
        # 得到当前摄像头拍摄的每一帧
        ret, frame = video_capture.read()

        # 缩放当前帧到4分支1大小，以加快识别进程的效率
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # 每次只处理当前帧的视频，以节省时间
        if process_this_frame:
            # 在当前帧中，找到所有的面部的位置以及面部的编码
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # 找到能够与已知面部匹配的面部
                match = face_recognition.compare_faces(face_encoding_list, face_encoding, 0.6)
                name = "Unknown"

                for i in range(0, len(match)):
                    if match[i]:
                        name = names_list[i]
                        face_names.append(name)

        process_this_frame = not process_this_frame

        # 显示结果
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # 将刚才缩放至4分支1的帧恢复到原来大小，并得到与每一个面部与姓名的映射关系
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # 在脸上画一个框框
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # 在框框的下边画一个label用于显示姓名
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.cv.CV_FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX

            # 在当前帧中显示我们识别的结果
            color_ = (255, 255, 255)
            pos = (left + 6, bottom - 6)
            text_size = 24
            # 使用自定义字体
            ft = ChineseTextUtil('zzz.ttc')
            image = ft.draw_text(frame, pos, name, text_size, color_)

            cv2.imshow('VideoZH', image)

            # cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            # cv2.imshow('Video', frame)

        # 按q退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    video_capture.release()
    cv2.destroyAllWindows()
# -*- coding: utf-8 -*-
import face_recognition
import cv2
from gevent import os
import freetype
import copy

from numpy import unicode


class ChineseTextUtil(object):
    def __init__(self, ttf):
        self._face = freetype.Face(ttf)

    def draw_text(self, image, pos, text, text_size, text_color):
        '''
        使用ttf字体库中的字体设置姓名
        :param image:     用于将text生成在某个image图像上
        :param pos:       画text的位置
        :param text:      unicode编码的text
        :param text_size: 字体大小
        :param text_color:字体颜色
        :return:          返回位图
        '''
        self._face.set_char_size(text_size * 64)
        metrics = self._face.size
        ascender = metrics.ascender / 64.0

        # descender = metrics.descender / 64.0
        # height = metrics.height / 64.0
        # linegap = height - ascender + descender
        ypos = int(ascender)

        if not isinstance(text, unicode):
            text = text.decode('utf-8')
        img = self.string_2_bitmap(image, pos[0], pos[1], text, text_color)
        return img

    def string_2_bitmap(self, img, x_pos, y_pos, text, color):
        '''
        将字符串绘制为图片
        :param x_pos: text绘制的x起始坐标
        :param y_pos: text绘制的y起始坐标
        :param text:  text的unicode编码
        :param color: text的RGB颜色编码
        :return:      返回image位图
        '''
        prev_char = 0
        pen = freetype.Vector()
        pen.x = x_pos << 6  # div 64
        pen.y = y_pos << 6

        hscale = 1.0
        matrix = freetype.Matrix(int(hscale) * 0x10000L, int(0.2 * 0x10000L), int(0.0 * 0x10000L), int(1.1 * 0x10000L))
        cur_pen = freetype.Vector()
        pen_translate = freetype.Vector()

        image = copy.deepcopy(img)
        for cur_char in text:
            self._face.set_transform(matrix, pen_translate)

            self._face.load_char(cur_char)
            kerning = self._face.get_kerning(prev_char, cur_char)
            pen.x += kerning.x
            slot = self._face.glyph
            bitmap = slot.bitmap

            cur_pen.x = pen.x
            cur_pen.y = pen.y - slot.bitmap_top * 64
            self.draw_ft_bitmap(image, bitmap, cur_pen, color)

            pen.x += slot.advance.x
            prev_char = cur_char

        return image

    def draw_ft_bitmap(self, img, bitmap, pen, color):
        '''
        draw each char
        :param bitmap: 位图
        :param pen:    画笔
        :param color:  画笔颜色
        :return:       返回加工后的位图
        '''
        x_pos = pen.x >> 6
        y_pos = pen.y >> 6
        cols = bitmap.width
        rows = bitmap.rows

        glyph_pixels = bitmap.buffer

        for row in range(rows):
            for col in range(cols):
                if glyph_pixels[row * cols + col] != 0:
                    img[y_pos + row][x_pos + col][0] = color[0]
                    img[y_pos + row][x_pos + col][1] = color[1]
                    img[y_pos + row][x_pos + col][2] = color[2]


if __name__ == '__main__':
    # 读取图片识别样例
    face_file_list = []
    names_list = []
    face_encoding_list = []

    rootdir = '/Users/z/Desktop/group_face1/'
    list = os.listdir(rootdir)
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isfile(path) and ".jpg" in list[i]:
            face_file_list.append(rootdir + list[i])
            print(list[i][:-4])
            names_list.append(list[i][:-4])

    for path in face_file_list:
        print(path)
        face_image = face_recognition.load_image_file(path)
        face_encoding = face_recognition.face_encodings(face_image)[0]
        face_encoding_list.append(face_encoding)

    # 初始化一些变量用于，面部位置，编码，姓名等
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    video_capture = cv2.VideoCapture(0)
    while True:
        # 得到当前摄像头拍摄的每一帧
        ret, frame = video_capture.read()

        # 缩放当前帧到4分支1大小，以加快识别进程的效率
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # 每次只处理当前帧的视频，以节省时间
        if process_this_frame:
            # 在当前帧中，找到所有的面部的位置以及面部的编码
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # 找到能够与已知面部匹配的面部
                match = face_recognition.compare_faces(face_encoding_list, face_encoding, 0.6)
                name = "Unknown"

                for i in range(0, len(match)):
                    if match[i]:
                        name = names_list[i]
                        face_names.append(name)

        process_this_frame = not process_this_frame

        # 显示结果
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # 将刚才缩放至4分支1的帧恢复到原来大小，并得到与每一个面部与姓名的映射关系
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # 在脸上画一个框框
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # 在框框的下边画一个label用于显示姓名
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.cv.CV_FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX

            # 在当前帧中显示我们识别的结果
            color_ = (255, 255, 255)
            pos = (left + 6, bottom - 6)
            text_size = 24
            # 使用自定义字体
            ft = ChineseTextUtil('zzz.ttc')
            image = ft.draw_text(frame, pos, name, text_size, color_)

            cv2.imshow('VideoZH', image)

            # cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            # cv2.imshow('Video', frame)

        # 按q退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    video_capture.release()
    cv2.destroyAllWindows()