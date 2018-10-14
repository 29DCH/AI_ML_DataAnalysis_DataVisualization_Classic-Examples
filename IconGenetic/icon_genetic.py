# -*- coding: utf-8 -*-
from __future__ import division
from PIL import Image as im
from random import randint
from copy import deepcopy
import pickle as pk

global_variable = {}


# 图片预处理
def process_pic(pic_name):
    print("正在初始化图片，将图片转换为颜色矩阵...")
    # 获得图片对象
    img = im.open(pic_name)
    # 获得图片的规格
    img_color = []
    img_width, img_height = img.size
    for x in range(img_height):
        img_color_tmp = []
        for y in range(img_width):
            # 图片的RGB
            r, g, b = img.getpixel((y, x))[:3]
            # 将RGB转10进制
            img_color_tmp.append((r, g, b, r + g + b))
        img_color.append(img_color_tmp)
    print("图片转化为颜色矩阵已完成")
    return img_color, img.size


# 随机产生第一代基因
def random_genes():
    print("当前图片尺寸：" + str(size))
    print("随机产生图像基因...")
    width, height = size
    genes = []
    for i in range(100):
        gene = []
        for x in range(height):
            row = []
            for y in range(width):
                a = randint(0, 255)
                b = randint(0, 255)
                c = randint(0, 255)
                row.append([a, b, c, a + b + c])
            gene.append(row)
        genes.append([gene, 0])
    print("图像基因已创建完毕...")
    return genes


# 定义适应度计算函数
def forecast():
    print("正在考察基因适应度...")
    sum_sum = 0
    for i, gene in enumerate(genes):
        sum_ = 0
        for j, row in enumerate(gene[0]):
            for k, col in enumerate(row):
                _a, _b, _c, _d = data[j][k]
                a, b, c, d = col
                det_d = abs(_d - d)
                sum_ += (abs(_a - a) + abs(_b - b) + abs(_c - c)) * det_d
        genes[i][1] = sum_
        sum_sum += sum_
    for i, gene in enumerate(genes):
        genes[i][1] = genes[i][1] / sum_sum
    print("基因正在排序...")
    genes.sort(key=lambda x: x[1])
    print("基因排序完成...")
    return


# 基因变异函数
def variation():
    rate = 0.5
    for i, gene in enumerate(genes):
        for x, row in enumerate(gene[0]):
            for y, col in enumerate(row):
                is_gene_mutation = False
                if randint(1, 100) / 100.0 <= rate:
                    is_gene_mutation = True
                    # 随机改变图片RGB的色值，a b c 分别对应 r_ g_ b_ 改变的值
                    a = [-1, 1][randint(0, 1)] * randint(5, 255)
                    b = [-1, 1][randint(0, 1)] * randint(5, 255)
                    c = [-1, 1][randint(0, 1)] * randint(5, 255)

                    genes[i][0][x][y][0] += a
                    genes[i][0][x][y][0] += b
                    genes[i][0][x][y][0] += c
                    genes[i][0][x][y][3] += a + b + c
    print("是否产生基因突变：" + str(is_gene_mutation))
    print("基因突变结束...")
    return


# 基因合并
def merge(gene1, gene2, p_size):
    width, height = p_size
    x = randint(0, height - 1)
    y = randint(0, width - 1)
    new_gene = deepcopy(gene1[0][:x])
    new_gene = [new_gene, 0]
    new_gene[0][x:] = deepcopy(gene2[0][x:])
    new_gene[0][x][:y] = deepcopy(gene1[0][x][:y])

    return new_gene


# 根据适应度函数的排序选择前2名优秀的基因
def select():
    print("基因淘汰选择中...")
    seek = int(len(genes) * 2.0 / 3)
    i = 0
    back_seek = seek + 1
    while i < seek:
        genes[back_seek] = merge(genes[i], genes[i + 1], size)
        back_seek += 1
        i += 2
    print("基因淘汰结束...")


# 生成图片的函数
def genera_pic(gene, genera):
    print("正在生成第 " + str(genera) + " 代的基因位图...")
    num = gene[1]
    gene = gene[0]
    img = im.open("swk.jpg")
    for y, row in enumerate(gene):
        for x, col in enumerate(row):
            a, b, c, d = col
            img.putpixel((x, y), (a, b, c))
    # if (genera - 1) % 100 == 0:
    img.save(str(genera) + ".jpg")


print("初始化基因进化程序...")
try:
    with open("intermediate_result.tmp", "rb") as fd:
        global_variable = pk.load(fd)
        data = global_variable["data"]
        size = global_variable["size"]
        genes = global_variable["genes"]
except:
    data, size = process_pic("swk.jpg")
    global_variable["data"] = data
    global_variable["size"] = size
    global_variable["genes"] = random_genes()
    global_variable["genera"] = 1
genes = deepcopy(global_variable["genes"])
print("基因进化程序已就绪...")


def main():
    global global_variable
    global genes
    global size
    genera = global_variable["genera"]
    while True:
        print("第 " + str(genera) + " 代基因")
        variation()
        forecast()
        variation()
        select()
        if genera % 20 == 0:
            global_variable["genes"] = genes
            global_variable["genera"] = genera
            genes = deepcopy(global_variable["genes"])
            with open("intermediate_result.tmp", "wb") as pt:
                pk.dump(global_variable, pt)

        if (genera - 1) % 100 == 0:
            genera_pic(genes[0], genera)

        for i in range(10):
            print("第 " + str(i) + " 个基因适应度为：" + str(genes[i][1]))
            genera += 1


def save_data():
    global global_variable
    print("输出文件...")
    with open("intermediate_result.tmp", "wb") as pt:
        pk.dump(global_variable, pt)
    print("文件输出已完成...")


if __name__ == '__main__':
    try:
        main()
    except:
        save_data()
