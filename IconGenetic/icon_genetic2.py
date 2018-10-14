from PIL import Image as im
from random import randint
from copy import deepcopy
import pickle as pk

# 全局变量
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


# 随机基因的函数
def random_genes(size):
    print("当前图片尺寸：", size, sep=" ")
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
def forecast(genes):
    print("正在计算基因适应度并排序...")
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
def variation(genes, size):
    rate = 0.5
    print("基因50%概率出现突变...")
    for i, gene in enumerate(genes):
        for x, row in enumerate(gene[0]):
            for y, col in enumerate(row):
                if randint(1, 100) / 100 <= rate:
                    # 随机改变图片RGB的色值，a b c 分别对应 r_ g_ b_ 改变的值
                    a = [-1, 1][randint(0, 1)] * randint(2, 10)
                    b = [-1, 1][randint(0, 1)] * randint(2, 10)
                    c = [-1, 1][randint(0, 1)] * randint(2, 10)

                    genes[i][0][x][y][0] += a
                    genes[i][0][x][y][0] += b
                    genes[i][0][x][y][0] += c
                    genes[i][0][x][y][3] += a + b + c
    print("基因突变结束...")
    return


# 基因合并
def merge(gene1, gene2, size):
    width, height = size
    x = randint(0, height - 1)
    y = randint(0, width - 1)
    new_gene = deepcopy(gene1[0][:x])
    new_gene = [new_gene, 0]
    new_gene[0][x:] = deepcopy(gene2[0][x:])
    new_gene[0][x][:y] = deepcopy(gene1[0][x][:y])

    return new_gene


# 根据适应度函数的排序选择前2名优秀的基因
def select(genes, size):
    print("基因淘汰选择中...")
    seek = int(len(genes) * 2 / 3)
    i = 0
    back_seek = seek + 1
    while i < seek:
        genes[back_seek] = merge(genes[i], genes[i + 1], size)
        back_seek += 1
        i += 2
    print("基因淘汰结束...")


# 生成图片的函数
def genera_pic(gene, genera):
    print("生成第", genera, "代的图片", sep=" ")
    num = gene[1]
    gene = gene[0]
    img = im.open("swk.jpg")
    for y, row in enumerate(gene):
        for x, col in enumerate(row):
            a, b, c, d = col
            img.putpixel((x, y), (a, b, c))
    img.save(str(genera) + "_" + str(num)[:6] + ".jpg")


try:
    print("初始化基因进化程序...")
    with open("intermediate_result.tmp", "rb") as pt:
        global_variable = pk.load(pt)
        data = global_variable["data"]
        size = global_variable["size"]
        genes = global_variable["genes"]
except:
    data, size = process_pic("swk.jpg")
    global_variable["data"] = data
    global_variable["size"] = size
    global_variable["genes"] = random_genes(size)
    global_variable["genera"] = 1
genes = deepcopy(global_variable["genes"])
print("基因进化程序已就绪...")


def main():
    global global_variable
    global genes
    global size
    genera = global_variable["genera"]
    while True:
        print("这是第", genera, "代基因", sep=" ")
        variation(genes, size)
        forecast(genes)
        variation(genes, size)
        select(genes, size)
        if genera % 20 == 0:
            global_variable["genes"] = genes
            global_variable["genera"] = genera
            genes = deepcopy(global_variable["genes"])
            with open("intermediate_result.tmp", "wb") as pt:
                pk.dump(global_variable, pt)

        if (genera - 1) % 10 == 0:
            genera_pic(genes[0], genera)

        for i in range(10):
            print("第", i, "个基因适应度为:", genes[i][1], sep=" ")
        genera += 1


def save_data():
    global global_variable
    print("输出文件...")
    with open("intermediate_result.tmp", "wb") as pt:
        pk.dump(global_variable, pt)
    print("文件输出已完成...")


try:
    main()
except:
    save_data()
