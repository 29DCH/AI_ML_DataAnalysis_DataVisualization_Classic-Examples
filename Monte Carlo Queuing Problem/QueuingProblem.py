import numpy as np

# 每个人到达队伍的时间，得到100个值
arrival_time = np.random.uniform(0, 3, size=100)
# 达到时间要排序，先来后到进行排队
arrival_time.sort()
# 排队时间为1~2分钟，得到100个值
duration_time = np.random.uniform(1, 2, size=100)

# 每个人排队起始时间
start_time = [0 for i in range(100)]
# 每个人排队结束时间
end_time = [0 for i in range(100)]
# 每个人等待时间
wait_time = [0 for i in range(100)]
# 每个位置空闲时间
empty_time = [0 for i in range(100)]

# 位置数量
queue_count = 50
pre_person_index = len(arrival_time) - len(arrival_time) // queue_count - 1
print(pre_person_index)

start_time[pre_person_index] = arrival_time[pre_person_index]
end_time[pre_person_index] = start_time[pre_person_index] + duration_time[pre_person_index]
wait_time[pre_person_index] = start_time[pre_person_index] - arrival_time[pre_person_index]


for i in range(pre_person_index + 1, len(arrival_time)):
    if end_time[i - 1] > arrival_time[i]:
        start_time[i] = end_time[i - 1]
    else:
        start_time[i] = arrival_time[i]
        empty_time[i] = start_time[i] - end_time[i - 1]

    end_time[i] = start_time[i] + duration_time[i]
    wait_time[i] = start_time[i] - arrival_time[i]
    print(wait_time[i])

print("每个人的平均等待时间: %f" % np.mean(wait_time))
