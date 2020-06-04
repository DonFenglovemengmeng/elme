from .dto import ActionNode, Courier, Order, Location
from .context import DispatchContext
from .util import DistanceUtils
from typing import Dict, List
import sys

class TailAppendPlan():
    def plan(self, courier: Courier, order: Order, context: DispatchContext):
        cp_list = courier.planRoutes
        if len(courier.orders) == 0:
            loc = courier.loc
            planTime = context.timeStamp
            loc_dst_list = []
            loc_src_list = [loc]
        else:
            loc_dst_list = courier.loc_dst_list
            loc_src_list = courier.loc_src_list
            lastNode = cp_list[-1]
            loc = context.orderPool.orderMap[lastNode.orderId].dstLoc
            planTime = lastNode.actionTime

        tailPlans, timeUUse = self.planOneOrder(courier, loc, planTime, order, loc_dst_list, loc_src_list)
        return cp_list+tailPlans, timeUUse

    def planOneOrder(self, courier: Courier, loc: Location, planTime, order: Order, loc_dst_list: List, loc_src_list: List):
        distanceUtils = DistanceUtils()
        is_over_time = False
        # Time_have = order.promiseDeliverTime - order.estimatedPrepareCompletedTime
        # if Time_have <= 0:
        #     Time_need = distanceUtils.timeConsuming(order.srcLoc, order.dstLoc, courier.speed)
        #     if Time_have < Time_need:
        #         is_over_time = True

        time_dst2dst = sys.float_info.max
        time_src2src = sys.float_info.max
        len_dst = len(loc_dst_list)
        len_src = len(loc_src_list)

        for i in range(max(len_dst, len_src)):
            if i < len_dst and time_dst2dst > 0:
                time_use_i = distanceUtils.timeConsuming(loc_dst_list[i], order.dstLoc, courier.speed)
                if time_dst2dst > time_use_i:
                    time_dst2dst = time_use_i
            if i < len_src and time_src2src > 0:
                time_use_i2 = distanceUtils.timeConsuming(loc_src_list[i], order.srcLoc, courier.speed)
                if time_src2src > time_use_i2:
                    time_src2src = time_use_i2
                    loc = loc_src_list[i]
            if time_dst2dst == 0 and time_src2src == 0:
                break

        time_dst2dst = time_dst2dst * len_dst + time_src2src * len_dst

        arrivalTime = distanceUtils.timeConsuming(loc, order.srcLoc, courier.speed)

        if len(courier.orders) == 0:
            time_dst2dst = arrivalTime / 3600
        else:
            if is_over_time:
                if time_dst2dst > 0:
                    time_dst2dst = sys.float_info.max

        # pickTime = 0 #max(order.estimatedPrepareCompletedTime, arrivalTime)
        # deliverTime = 0 #pickTime + distanceUtils.timeConsuming(order.srcLoc, order.dstLoc, courier.speed)
        arrivalNode = ActionNode(1, order.id, arrivalTime, False, planTime, time_dst2dst)
        pickNode = ActionNode(2, order.id, 0, False, arrivalTime, time_dst2dst)
        deliveryNode = ActionNode(3, order.id, 0, False, 0, time_dst2dst)
        return [arrivalNode, pickNode, deliveryNode], time_dst2dst