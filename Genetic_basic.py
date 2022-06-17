import sys, random, bisect


def find_height(graph):
    num = len(graph[0])
    h = [-1 for i in range(num)]
    children = graph[0]
    parents = graph[1]
    for i in range(num):
        if h[i] == -1:
            S = [i]
            while S:
                temp = S[-1]
                if h[temp] != -1:
                    S.pop()
                    h[temp] = 1 + (max(h[j] for j in parents[temp] or [-1]))
                else:
                    h[temp] = 0
                    S.extend([j for j in parents[temp] if h[j] == -1])
    maxi = max(h)
    out = []
    for i in range(num):
        mini = min([h[j] for j in children[i]] or [maxi + 1]) - 1
        out.append(random.randint(h[i], mini))
    return out


def task_partition(num, height):
    G = [[] for i in range(max(height)+1)]
    for i in range(num):
        G[height[i]].append(i)
    return G


def form_schedule(proc_num, G):
    schedule = [[] for i in range(proc_num)]
    for gtask in G:
        procs = list(range(proc_num))
        random.shuffle(gtask)
        random.shuffle(procs)
        for i in range(proc_num-1):
            r = random.randint(0, len(gtask))
            schedule[procs[i]].extend(gtask[-r:])
            gtask = gtask[:-r]
        schedule[procs[-1]].extend(gtask)
    return schedule


def finishing_time(graph, schedule, times):
    num = len(graph[0])
    parents = graph[1]
    pos = [(-1, -1) for i in range(num)]
    for i in range(len(schedule)):
        for j in range(len(schedule[i])):
            pos[schedule[i][j]] = (i, j)
    for i in pos:
        assert i != (-1, -1)
    time_tasks = [-1] * num
    for i in range(num):
        if time_tasks[i] == -1:
            S = []
            S.append(i)
            while S:
                task = S[-1]
                x, y = pos[task]
                ptask = schedule[x][y-1] if y else -1
                if time_tasks[task] != -1:
                    S.pop()
                    min_par = max([time_tasks[j] for j in parents[task]] or [0])
                    mini = min_par if y == 0 else max(min_par, time_tasks[ptask])
                    time_tasks[task] = times[task] + mini
                else:
                    time_tasks[task] = 0
                    if y:
                        S.append(ptask)
                    for j in parents[task]:
                        if time_tasks[j] == -1 and j != ptask:
                            S.append(j)
    return max(time_tasks)


def legal_task(schedules, height):
    for schedule in schedules:
        assert len(height) == sum(len(proc) for proc in schedule)
        for proc in schedule:
            for i in range(len(proc) - 1):
                assert height[proc[i]] <= height[proc[i+1]]


def reproduction(schedules, fitness_value):
    num = len(schedules)
    fitness_sum = sum(fitness_value)
    wheel = []
    Sum = 0
    new = []
    for i in range(num):
        Sum = Sum + fitness_value[i]
        wheel.append(Sum)
    for i in range(num):
        select = random.randint(1, fitness_sum)
        select_index = bisect.bisect_left(wheel, select)
        new.append(schedules[select_index])
    return new


def pop_schedule(schedules):
    index = random.randint(0, len(schedules)-1)
    schedules[-1], schedules[index] = schedules[index], schedules[-1]
    return schedules.pop()


def crossover(sch1, sch2, height):
    proc_num = len(sch1)
    maxi_height = max(height)
    p = random.randint(0, maxi_height)
    newsch1 = [([nd for nd in sch1[i] if height[nd] <= p]+[nd for nd in sch2[i] if height[nd] > p]) for i in range(proc_num)]
    newsch2 = [([nd for nd in sch2[i] if height[nd] <= p]+[nd for nd in sch2[i] if height[nd] > p]) for i in range(proc_num)]
    return newsch1, newsch2


def search_task(s, task):
    num = len(s)
    for i in range(num):
        for j in range(len(s[i])):
            if s[i][j] == task:
                return i, j
    assert False


def mutation(s, height):
    num = len(s)
    task1 = random.randint(0, num - 1)
    candidates = [i for i in range(num) if height[i] == height[task1] and i != task1]
    if not candidates:
        return
    task2 = random.choice(candidates)
    x, y = search_task(s, task1)
    a, b = search_task(s, task2)
    s[x][y], s[a][b] = s[a][b], s[x][y]
    return


def genetic_schedule(graph, proc_num, times, pop_size, iterations_num):
    num = len(graph[0])
    iterations = 0
    height = find_height(graph)
    tasksets = task_partition(num, height)
    POP = [form_schedule(proc_num, tasksets) for i in range(pop_size)]
    finish_time = [finishing_time(graph, s, times) for s in POP]
    best_time = 0
    while iterations != iterations_num:
        legal_task(POP, height)
        maxi, mini = max(finish_time), min(finish_time)
        fitness_value = [(maxi - t) + 1 for t in finish_time]
        best_string = POP[finish_time.index(mini)]
        new_schedules = reproduction(POP, fitness_value)
        temp = []
        for i in range(int(pop_size/2)):
            sch1 = pop_schedule(new_schedules)
            sch2 = pop_schedule(new_schedules)
            sch1, sch2 = crossover(sch1, sch2, height)
            temp.append(sch1)
            temp.append(sch2)
        POP = []
        for s in temp:
            select = random.randint(1, 200)
            if select == 1:
                mutation(s, height)
            POP.append(s)
        best_time = finishing_time(graph, best_string, times)
        finish_time = [finishing_time(graph, s, times) for s in POP]
        max_index = finish_time.index(max(finish_time))
        POP[max_index] = best_string
        finish_time[max_index] = best_time
        iterations = iterations + 1
    return str(best_time)


with open(r'./测试数据/rand0000.txt', 'r') as files:
    temp = list(map(int, files.readline().split(' ')))
    task_num = temp[0]
    edge_num = 0
    task_time = []
    graph = [[] for i in range(task_num)], [[] for i in range(task_num)]
    for i in range(task_num):
        data = list(map(int, files.readline().split('         ')))
        task_time.append(data[1])
        for j in range(data[2]):
            father, child = data[3 + j] - 1, data[0] - 1
            if father == -1:
                continue
            edge_num += 1
            graph[0][father].append(child)
            graph[1][child].append(father)
files.close()
best = genetic_schedule(graph, 4, task_time, 20, 1000)
sys.stdout.write(best + "\n")



