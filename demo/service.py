from .dto import DispatchRequest, DispatchSolution, ActionNode, CourierPlan
from .context import DispatchContext
from typing import Dict, List
from .solver import BaseSolver

class DispatchService:
    def __init__(self):
        self.serviceContext: Dict[str, DispatchContext] = {}

    def dispatch(self, request: DispatchRequest):
        areaId = request.areaId
        if request.isFirstRound:
            context = DispatchContext(areaId, request.requestTimestamp)
            self.serviceContext[areaId] = context
        else:
            context = self.serviceContext.get(areaId)
            if context is None:
                emptySolution = DispatchSolution([])
                return emptySolution
            else:
                if request.isLastRound:
                    context.setIsEndOfTest(True)
            context.refresh(request.requestTimestamp)

        context.addOnlineCouriers(request.couriers)
        context.addDispatchingOrders(request.orders)
        # --------------------------------------------------------------------------------------------------------------
        if not context.isEndOfTest:
            for cu in context.courierPool.couriers:
                order_list_cu = []
                for cp in cu.planRoutes:
                    if not cp.isSubmitted and cp.actionType == 1:
                        order_list_cu.append(cp.orderId)
                order_redispath = []
                for ii in range(len(order_list_cu)):
                    tim_use_ = 0
                    for cp in cu.planRoutes:
                        is_break = False
                        if order_list_cu[ii] == cp.orderId:
                            tim_use_ += cp.timeUse
                            if cp.actionType == 3:
                                is_break = True
                                if context.orderPool.orderMap[order_list_cu[ii]].promiseDeliverTime - cp.actionTime < 0:
                                    if not (context.orderPool.orderMap[order_list_cu[ii]].promiseDeliverTime - request.requestTimestamp < 0 and tim_use_ == 0):
                                        order_redispath.append(order_list_cu[ii])
                                        context.orderPool.restOrder(order_list_cu[ii])
                        if is_break:
                            break
                if len(order_redispath) > 0:
                    cu.setsetPlanRoutes([p for p in cu.planRoutes if p.orderId not in order_redispath])
                    cu.setsetorders([o for o in cu.orders if o.id not in order_redispath])
        # --------------------------------------------------------------------------------------------------------------
        solver = self.getSolver(context)
        courierPlans = solver.solve()
        for cp in courierPlans:
            for a in cp.planRoutes:
                a.setSubmitted(True)
        assignedIds = solver.getAssignedOrderIds()
        context.markAllocatedOrders(assignedIds)
        while len(context.orderPool.getDispatchingOrders()) != 0 and context.isEndOfTest:
            aheadTime = 10 * 60
            context.setTimeStamp(context.timeStamp + aheadTime)
            lastRoundSolver = self.getSolver(context)
            tmpPlans = lastRoundSolver.solve()
            for cp in tmpPlans:
                for a in cp.planRoutes:
                    a.setSubmitted(True)
            context.markAllocatedOrders(lastRoundSolver.getAssignedOrderIds())
        solution = DispatchSolution(courierPlans)
        return solution

    def getSolver(self, context: DispatchContext) -> BaseSolver:
        return BaseSolver(context)



