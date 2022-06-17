import sys, random
import bisect, copy


def form_schedule(task_num, proc_num, graph):
    schedule = [[] for i in range(proc_num)]
    available = []
    graph1 = copy.deepcopy(graph)
    for i in range(task_num):
        if not graph1[1][i]:
            available.append(i)
    iteration = task_num
    while iteration != 0:
        avail_num = len(available)
        t = random.randint(0, avail_num - 1)
        p = random.randint(0, proc_num - 1)
        schedule[p].append(available[t])
        for i in graph1[0][available[t]]:
            if len(graph1[1][i]) == 1:
                available.append(i)
            graph1[1][i].remove(available[t])
        available.remove(available[t])
        iteration -= 1
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


def search_task(s, task):
    num = len(s)
    for i in range(num):
        for j in range(len(s[i])):
            if s[i][j] == task:
                return i, j
    assert False


def find_Ds(D, s):
    Ds = copy.deepcopy(D)
    for i in range(len(D)):
        for j in range(len(D)):
            if D[i][j] != 1 and i != j:
                p1, r1 = search_task(s, i)
                p2, r2 = search_task(s, j)
                if p1 == p2 and r1 == (r2 - 1):
                    Ds[i][j] = 1
    return Ds


def find_transitive_closure(D):
    n = len(D)
    DT = copy.deepcopy(D)
    #print("DT",DT)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                DT[i][j] = DT[i][j] or (DT[i][k] and DT[k][j])
    #print(DT)
    return DT


def partition(task_num, Ds1, Ds2):
    T = list(range(task_num))
    V1, V2 = [], []
    Ds = [[0 for a in range(task_num)]for x in range(task_num)]
    for x in range(task_num):
        for y in range(task_num):
            Ds[x][y] = Ds1[x][y] or Ds2[x][y]
    DT = find_transitive_closure(Ds)
    while len(T) != 0:
        r = random.randint(0, len(T) - 1)
        q = random.randint(1, 2)
        delete = []
        if q == 1:
            V1.append(T[r])
            for i in range(len(T)):
                if T[i] != T[r]:
                    if DT[T[i]][T[r]] == 1:
                        V1.append(T[i])
                        delete.append(T[i])
            delete.append(T[r])
        else:
            V2.append(T[r])
            for i in range(len(T)):
                if T[i] != T[r]:
                    if DT[T[r]][T[i]] == 1:
                        V2.append(T[i])
                        delete.append(T[i])
            delete.append(T[r])
        for k in delete:
            T.remove(k)
    assert len(V1) + len(V2) == task_num
    assert len(T) == 0
    return V1, V2


def crossover(D, sch1, sch2):
    #print("sch")
    #print(sch1,'\n',sch2)
    proc_num = len(sch1)
    Ds1, Ds2 = find_Ds(D, sch1), find_Ds(D, sch2)
    V1, V2 = partition(len(D), Ds1, Ds2)
    #print("V1,V2")
    #print(V1)
    #print(V2)
    for i in range(proc_num):
        c1 = 0
        c2 = 0

        for j in range(len(sch1[i]) - 1):
            if sch1[i][j] in V1 and sch1[i][j + 1] in V2:
                c1 = j + 1
        if not sch1[i]:
            c1 = 0
        elif sch1[i][-1] in V1:
            c1 = len(sch1[i])
        for j in range(len(sch2[i]) - 1):
            if sch2[i][j] in V1 and sch2[i][j + 1] in V2:
                c2 = j + 1
        if not sch2[i]:
            c2 = 0
        elif sch2[i][-1] in V1:
            c2 = len(sch2[i])

        #print(c1, c2)

        if c1 < len(sch1[i]):
            t1 = sch1[i][c1:]
        else:
            t1 = []
        if c2 < len(sch2[i]):
            t2 = sch2[i][c2:]
        else:
            t2 = []

        if c1 == 0:
            sch1[i] = t2
        elif c1 == len(sch1[i]):
            sch1[i].extend(t2)
        else:
            sch1[i][c1:] = t2
        if c2 == 0:
            sch2[i] = t1
        elif c2 == len(sch2[i]):
            sch2[i].extend(t1)
        else:
            sch2[i][c2:] = t1

    return sch1, sch2


def mutation(s):
    return s


def genetic_schedule(graph, proc_num, times, pop_size, iterations_num):
    num = len(graph[0])
    iterations = 0
    pop = [form_schedule(num, proc_num, graph) for i in range(pop_size)]
    finish_time = [finishing_time(graph, s, times) for s in pop]
    best_time = 0
    while iterations != iterations_num:
        maxi, mini = max(finish_time), min(finish_time)
        fitness_value = [(maxi - t) + 1 for t in finish_time]
        best_string = pop[finish_time.index(mini)]
        new_schedules = reproduction(pop, fitness_value)
        temp_pop = []
        for i in range(int(pop_size/2)):
            sch1 = pop_schedule(new_schedules)
            sch2 = pop_schedule(new_schedules)
            sch1, sch2 = crossover(D, sch1, sch2)
            temp_pop.append(sch1)
            temp_pop.append(sch2)
        pop = []
        for s in temp_pop:
            select = random.randint(1, 20)
            if select == 1:
                mutation(s)
            pop.append(s)
        best_time = finishing_time(graph, best_string, times)
        finish_time = [finishing_time(graph, s, times) for s in pop]
        max_index = finish_time.index(max(finish_time))
        pop[max_index] = best_string
        finish_time[max_index] = best_time
        iterations = iterations + 1
    return str(best_time)


with open(r'./测试数据/rand0000.txt', 'r') as files:
    temp = list(map(int, files.readline().split(' ')))
    task_num = temp[0]
    edge_num = 0
    task_time = []
    graph = [[] for i in range(task_num)], [[] for i in range(task_num)]
    D = [[0 for i in range(task_num)] for j in range(task_num)]
    for i in range(task_num):
        data = list(map(int, files.readline().split('         ')))
        task_time.append(data[1])
        for j in range(data[2]):
            father, child = data[3 + j] - 1, data[0] - 1
            if father == -1:
                continue
            D[father][child] = 1
            edge_num += 1
            graph[0][father].append(child)
            graph[1][child].append(father)
files.close()
best = genetic_schedule(graph, 4, task_time, 20, 500)
sys.stdout.write(best + "\n")



