from .context import DispatchContext
from .dto import Courier, Order, CourierPlan, ActionNode
from typing import Dict, List
from .plan import TailAppendPlan
from .util import DistanceUtils
import sys


class Cost:
    def __init__(self, i, j, couriers: List[Courier], orders: List[Order], context: DispatchContext):
        self.i = i
        self.j = j
        self.courier = couriers[i]
        self.order = orders[j]
        tailAppendPlan = TailAppendPlan()
        self.planActionNodes, self.timeUUUUse = tailAppendPlan.plan(self.courier, self.order, context)
        self.cost = self.calCost()

    def isValid(self):
        maxLoad = self.courier.maxLoads
        cr = sum([1 for order in self.courier.orders if order.status == 3])
        for node in self.planActionNodes:
            if node.actionType == 2:
                cr += 1
                if cr > maxLoad:
                    return False
            if node.actionType == 3:
                cr -= 1
        return True

    def calCost(self):
        cost = self.timeUUUUse
        if not self.isValid():
            return sys.float_info.max
        return cost


class BaseSolver:
    def __init__(self, context: DispatchContext):
        self.context = context
        self.orders = self.getCandidateOrders(context)
        self.couriers = self.getCandidateCouriers(context)
        self.ordersAssigned = [False for i in self.orders]
        self.costTable = []
        self.MINIMUM_INTERVAL_SECONDS = 60

    def getCandidateCouriers(self, dispatchContext: DispatchContext):
        return dispatchContext.courierPool.couriers

    def getCandidateOrders(self, dispatchContext: DispatchContext):
        return dispatchContext.orderPool.getDispatchingOrders()

    def getAssignedOrderIds(self):
        return [order.id for i, order in enumerate(self.orders) if self.ordersAssigned[i]]

    def initTable(self):
        def init_cp(cooooo):
            list_yes = []
            list_no = {}
            order_list = {}
            loc_dst_list = []
            loc_src_list = []
            for node in cooooo.planRoutes:
                if node.isSubmitted:
                    list_yes.append(node)
                else:
                    list_no[str(node.actionType) + "_" + str(node.orderId)] = node
                    order_list[str(node.orderId)] = node.orderId
                    if node.actionType == 3:
                        loc_dst_list.append(self.context.orderPool.orderMap[node.orderId].dstLoc)
                    if node.actionType == 2:
                        loc_src_list.append(self.context.orderPool.orderMap[node.orderId].srcLoc)
            cooooo.set_node_submit(list_yes)
            cooooo.set_node_not_submit(list_no)
            cooooo.set_order_list(order_list)
            if len(list_yes) > 0:
                loc_dst_list += [self.context.orderPool.orderMap[list_yes[-1].orderId].dstLoc]
                if list_yes[-1].actionType == 3:
                    loc_src_list += [self.context.orderPool.orderMap[list_yes[-1].orderId].dstLoc]
                else:
                    loc_src_list += [self.context.orderPool.orderMap[list_yes[-1].orderId].srcLoc]
            else:
                #loc_dst_list += [cooooo.loc]
                loc_src_list += [cooooo.loc]
            cooooo.set_loc_dst_list(loc_dst_list)
            cooooo.set_loc_src_list(loc_src_list)

        courierSize = len(self.couriers)
        orderSize = len(self.orders)
        for i in range(courierSize):
            init_cp(self.couriers[i])
            costTableRow = []
            for j in range(orderSize):
                costTableRow.append(self.getCost(i, j))
            self.costTable.append(costTableRow)

    def solve(self) -> List[CourierPlan]:
        self.initTable()
        while True:
            cost = self.getBest()
            if cost is None:
                break
            self.dealWithCost(cost)
        results: List[CourierPlan] = []
        for courier in self.couriers:
            self.optimization_Plan(courier)
            submitPlan = self.getSubmitPlan(courier)
            if len(submitPlan.planRoutes) != 0:
                results.append(submitPlan)
        return results

    def optimization_Plan(self, courier):
        def find_node_list(node, node_map):
            def find_ij(node, i, j):
                node_new = node[:]
                temp = node_new[i]
                node_new[i] = node_new[j]
                node_new[j] = temp
                return node_new

            def check_ij(node, rule_):
                check_rule = True
                for i in range(len(node)):
                    for k in range(i + 1, len(node)):
                        if rule_[node[i]] - rule_[node[k]] == 1:
                            check_rule = False
                            break
                return check_rule

            def find_timeuse(node_ij, node_map):
                time_use = 0
                for i in range(len(node_ij) - 1):
                    time_use += node_map[i][i + 1]
                return time_use

            len_node = len(node)
            rule_ = {}
            for i in range(len_node):
                if i % 2 == 0:
                    rule_[node[i]] = (i + 2) / 2 * 10
                else:
                    rule_[node[i]] = (i + 1) / 2 * 10 + 1
            node_best = node
            time_best = find_timeuse(node_best, node_map)
            for i in range(1, len_node):
                for j in range(len_node):
                    if i != j:
                        node_ij = find_ij(node, i, j)
                        if check_ij(node_ij, rule_):
                            time_ij = find_timeuse(node_ij, node_map)
                            if time_best > time_ij:
                                time_best = time_ij
                                node_best = node_ij
            return node_best
        def get_loc(node__):
            node_i_oid = self.context.orderPool.orderMap[node__.orderId]
            if node__.actionType == 3:
                _loc = node_i_oid.dstLoc
            else:
                _loc = node_i_oid.srcLoc
            return _loc
        def find_plan_node(_plan_sub_N, _order_list, start_loc, start_Time):
            time__i = sys.float_info.max
            time__i_arf = sys.float_info.max
            key_del = ''
            New_node_res = None
            for key_o in _order_list:
                temp_node = None
                key_ = ''
                actionType_min = 80
                count_key_i = 0
                for key_i in _plan_sub_N:
                    node = _plan_sub_N[key_i]
                    if node.orderId == _order_list[key_o]:
                        if actionType_min > node.actionType:
                            actionType_min = node.actionType
                            temp_node = node
                            key_ = key_i
                            count_key_i += 1
                    if count_key_i == 3:
                        break
                    if actionType_min == 1:
                        break
                if key_ != '':
                    time_need = distanceUtils.timeConsuming(start_loc, get_loc(temp_node), courier.speed)
                    time_arf = time_need + start_Time
                    if temp_node.actionType != 3:
                        a_time = max(self.context.orderPool.orderMap[temp_node.orderId].estimatedPrepareCompletedTime,time_arf)
                        time_arf = a_time + (a_time - time_arf)
                    if time_need > 0 and temp_node.actionType == 3:
                        if self.context.orderPool.orderMap[temp_node.orderId].promiseDeliverTime - time_arf < 0:
                            time_arf += time_need
                    if time__i_arf > time_arf:
                        time__i_arf = time_arf
                        time__i = time_need
                        New_node_res = temp_node
                        key_del = key_
            return New_node_res, time__i, key_del
        _plan_sub_N, _order_list = courier.node_not_submit, courier.order_list
        if len(_plan_sub_N) >= 1:
            _plan_sub_Y = courier.node_submit
            _plan_sub_N_new = []
            distanceUtils = DistanceUtils()
            if len(_plan_sub_N) >= 1:
                last_node_list = None
                is_first_node = False
                if len(_plan_sub_N_new) == 0:
                    if len(_plan_sub_Y) == 0:
                        is_first_node = True
                    else:
                        last_node_list = _plan_sub_Y[-1]
                else:
                    last_node_list = _plan_sub_N_new[-1]

                while len(_plan_sub_N) > 0:
                    if is_first_node:
                        start_loc = courier.loc
                        start_Time = self.context.timeStamp
                        is_first_node = False
                    else:
                        lastNode = last_node_list
                        start_loc = get_loc(lastNode)
                        start_Time = lastNode.actionTime

                    Node_new, time__i, key_del = find_plan_node(_plan_sub_N, _order_list, start_loc, start_Time)
                    _actionTimestamp = start_Time + time__i
                    if Node_new.actionType == 2:
                        _actionTimestamp = max(self.context.orderPool.orderMap[Node_new.orderId].estimatedPrepareCompletedTime,_actionTimestamp)
                    New_Node = ActionNode(Node_new.actionType, Node_new.orderId, _actionTimestamp, False, start_Time, time__i)
                    _plan_sub_N_new.append(New_Node)
                    last_node_list = New_Node
                    del _plan_sub_N[key_del]
                    if key_del.split('_')[0] == '3':
                        del _order_list[key_del.split('_')[1]]
            else:
                aa__plan_sub_N = _plan_sub_N
                node_idx = [i for i in range(len(aa__plan_sub_N))]
                node_map = []
                for _i in range(len(aa__plan_sub_N)):
                    node_map_i = []
                    start_loc = get_loc(aa__plan_sub_N[_i])
                    for _j in range(len(aa__plan_sub_N)):
                        if _i == _j:
                            node_map_i.append(0)
                        else:
                            node_map_i.append(distanceUtils.timeConsuming(start_loc, get_loc(aa__plan_sub_N[_j]), courier.speed)+1)
                    node_map.append(node_map_i)
                node_idx = find_node_list(node_idx, node_map)
                for ii in range(len(node_idx)):
                    if ii == 0:
                        if len(_plan_sub_Y) == 0:
                            start_loc = courier.loc
                            start_Time = self.context.timeStamp
                        else:
                            lastNode = _plan_sub_Y[-1]
                            start_loc = get_loc(lastNode)
                            start_Time = lastNode.actionTime
                    else:
                        lastNode = _plan_sub_N_new[-1]
                        start_loc = get_loc(lastNode)
                        start_Time = lastNode.actionTime
                    Node_new = aa__plan_sub_N[node_idx[ii]]

                    if ii == 0:
                        time_use = distanceUtils.timeConsuming(start_loc, get_loc(Node_new), courier.speed)
                    else:
                        time_use = node_map[node_idx[ii-1]][node_idx[ii]]

                    _actionTimestamp = start_Time + time_use
                    if Node_new.actionType == 2:
                        _actionTimestamp = max(self.context.orderPool.orderMap[Node_new.orderId].estimatedPrepareCompletedTime, _actionTimestamp)
                    if Node_new.actionType == 1:
                        time_wait = _actionTimestamp - self.context.orderPool.orderMap[Node_new.orderId].estimatedPrepareCompletedTime
                        if time_wait < 0:
                            start_Time = start_Time - time_wait
                            _actionTimestamp = _actionTimestamp - time_wait
                    New_Node = ActionNode(Node_new.actionType, Node_new.orderId, _actionTimestamp, False, start_Time, 0)
                    _plan_sub_N_new.append(New_Node)
            # ------------------------------
            courier.setsetPlanRoutes(_plan_sub_Y + _plan_sub_N_new)
            return courier
        else:
            return courier

    def getSubmitPlan(self, courier: Courier):
        submitThresholdTime = self.context.timeStamp + self.MINIMUM_INTERVAL_SECONDS
        submittedNodes = [node for node in courier.planRoutes if (not node.isSubmitted) and (node.needSubmitTime <= submitThresholdTime or self.context.isEndOfTest)]
        plan = CourierPlan(courier.id, submittedNodes)
        return plan

    def dealWithCost(self, cost: Cost):
        cost.courier.setsetPlanRoutes(cost.planActionNodes)
        cost.courier.orders.append(cost.order)
        cost.courier.loc_dst_list.append(cost.order.dstLoc)
        cost.courier.loc_src_list.append(cost.order.srcLoc)
        for node_c in cost.planActionNodes[-3:]:
            cost.courier.node_not_submit[str(node_c.actionType) + "_" + str(node_c.orderId)] = node_c
            cost.courier.order_list[str(node_c.orderId)] = node_c.orderId
        self.ordersAssigned[cost.j] = True
        self.updateWeightRow(cost.i)
        self.updateWeightCol(cost.j)

    def updateWeightRow(self, i):
        for j in range(len(self.orders)):
            self.costTable[i][j] = self.getCost(i, j)

    def updateWeightCol(self, j):
        for i in range(len(self.couriers)):
            self.costTable[i][j] = self.getCost(i, j)

    def getBest(self):
        best = None
        courierSize = len(self.couriers)
        orderSize = len(self.orders)
        for i in range(courierSize):
            for j in range(orderSize):
                tmpC = self.costTable[i][j]
                if tmpC is None:
                    continue
                if best is None:
                    best = tmpC
                    continue
                if self.costLess(tmpC, best):
                    best = tmpC
        return best

    def costLess(self, c1: Cost, c2: Cost):
        return c1.cost <= c2.cost

    def getCost(self, i, j):
        if self.ordersAssigned[j]:
            return None
        cost = Cost(i, j, self.couriers, self.orders, self.context)
        if not cost.isValid():
            return None
        return cost
