from typing import Dict, List

class Location(object):
    def __init__(self, _latitude, _longitude):
        self.latitude = _latitude
        self.longitude = _longitude

    def keys(self):
        return ['latitude', 'longitude']

    def __getitem__(self, item):
        return getattr(self, item)


class Courier(object):
    def __init__(self, _id, _areaId, _loc, _speed, __maxLoads):
        self.id = _id
        self.areaId = _areaId
        self.loc = _loc
        self.speed = _speed
        self.maxLoads = __maxLoads

        self.planRoutes: List[ActionNode] = []
        self.orders: List[Order] = []
        self.node_submit = []
        self.node_not_submit = {}
        self.order_list = {}
        self.loc_dst_list = []
        self.loc_src_list = []

    def keys(self):
        return ['id', 'areaId', 'loc', 'speed', 'maxLoads']

    def __getitem__(self, item):
        return getattr(self, item)

    def setLoc(self, loc):
        self.loc = loc

    def setsetPlanRoutes(self, _planRoutes):
        self.planRoutes = _planRoutes

    def setsetorders(self, _orders):
        self.orders = _orders

    def set_node_submit(self, _node_yes):
        self.node_submit = _node_yes

    def set_node_not_submit(self, _node_no):
        self.node_not_submit = _node_no

    def set_order_list(self, _order_list):
        self.order_list = _order_list

    def set_loc_src_list(self, _loc_src_list):
        self.loc_src_list = _loc_src_list

    def set_loc_dst_list(self, _loc_dst_list):
        self.loc_dst_list = _loc_dst_list

class Order(object):
    def __init__(self, _areaId, _id, _srcLoc, _dstLoc, _status, _createTimestamp, _promiseDeliverTime,
                 _estimatedPrepareCompletedTime):
        self.areaId = _areaId
        self.id = _id
        self.srcLoc = _srcLoc
        self.dstLoc = _dstLoc
        self.status = _status
        self.createTimestamp = _createTimestamp
        self.promiseDeliverTime = _promiseDeliverTime
        self.estimatedPrepareCompletedTime = _estimatedPrepareCompletedTime

    def keys(self):
        return ['id', 'areaId', 'srcLoc', 'dstLoc', 'status',
                'createTimestamp', 'promiseDeliverTime', 'estimatedPrepareCompletedTime']

    def __getitem__(self, item):
        return getattr(self, item)

    def setStatus(self, status):
        self.status = status


class ActionNode(object):
    def __init__(self, _actionType, _orderId, _actionTimestamp, _isSubmitted, _needSubmitTime, _time_use):
        self.actionTime = _actionTimestamp
        self.actionType = _actionType
        self.orderId = _orderId
        if _isSubmitted is None:
            self.isSubmitted = False
        else:
            self.isSubmitted = _isSubmitted
        if _needSubmitTime is None:
            self.needSubmitTime = -1
        else:
            self.needSubmitTime = _needSubmitTime
        # if _time_use is None:
        #     self.timeUse = -1
        # else:
        #     self.timeUse = _time_use
        self.timeUse = _time_use

    def keys(self):
        return ['actionType', 'orderId', 'actionTimestamp', 'isSubmitted', 'needSubmitTime', 'timeUse']

    def __getitem__(self, item):
        return getattr(self, item)

    def setSubmitted(self, _isSubmitted):
        self.isSubmitted = _isSubmitted

    def setactionTime(self, _actionTime):
        self.actionTime = _actionTime

    def setneedSubmitTime(self, _needSubmitTime):
        self.needSubmitTime = _needSubmitTime

    def settimeAll(self, _timeAll):
        self.timeAll = _timeAll

class CourierPlan(object):
    def __init__(self, _courierId, _planRoutes):
        self.courierId = _courierId
        self.planRoutes: List[ActionNode] = _planRoutes

    def keys(self):
        return ['courierId', 'planRoutes']

    def __getitem__(self, item):
        return getattr(self, item)

    def setsetPlanRoutes(self, _planRoutes):
        self.planRoutes = _planRoutes


class DispatchRequest(object):
    def __init__(self, _requestTimestamp, _areaId, _isFirstRound, _isLastRound, _couriers, _orders):
        self.requestTimestamp = _requestTimestamp
        self.areaId = _areaId
        self.isFirstRound = _isFirstRound
        self.isLastRound = _isLastRound
        self.couriers = _couriers
        self.orders = _orders

    def keys(self):
        return ['requestTimestamp', 'areaId', 'isFirstRound', 'isLastRound',
                'couriers', 'orders']

    def __getitem__(self, item):
        return getattr(self, item)


class DispatchSolution(object):
    def __init__(self, _courierPlans):
        self.courierPlans = _courierPlans

    def keys(self):
        return ['courierPlans']

    def __getitem__(self, item):
        return getattr(self, item)


class Response(object):
    def __init__(self, _code, _result, _message):
        self.code = _code
        self.result = _result
        self.message = _message

    def keys(self):
        return ['code', 'result', 'message']

    def __getitem__(self, item):
        return getattr(self, item)
