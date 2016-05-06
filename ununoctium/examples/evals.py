import geon.backends.graph.evaluation as evaluation
import numpy as np
import geon.backends.graph.cudagpu as cudagpu
import geon.backends.graph.funs as be

class Eval(be.Model):
    def __init__(self, **kargs):
        super(Eval, self).__init__(**kargs)
        a = self.a
        a.S[10]
        g = self.graph

        g.x = be.input(axes=(a.S,))
        g.y = be.input(axes=(a.S,))
        g.w = be.deriv(g.x + g.y, g.y)
        g.x2 = be.dot(g.x, g.x)

        g.z = 2 * be.deriv(be.exp(abs(-be.log(g.x * g.y))), g.x)

    @be.with_graph_context
    @be.with_environment
    def run(self):
        x = np.arange(10, dtype=np.float32) + 1
        y = x * x

        self.graph.x.value = be.ArrayWithAxes(x, (self.a.S,))
        self.graph.y.value = be.ArrayWithAxes(y, (self.a.S,))

        gnp = evaluation.GenNumPy(results=(self.graph.x2, self.graph.z, self.graph.w))
        gnp.evaluate()

        enp = evaluation.NumPyEvaluator(results=(self.graph.x2, self.graph.z, self.graph.w))
        resultnp = enp.evaluate()
        print resultnp

        # epc = evaluation.PyCUDAEvaluator(results=(self.naming.z, self.naming.w))
        # epc.set_input(self.naming.x, xa)
        # epc.set_input(self.naming.y, ya)
        # resultpc = epc.evaluate()
        # with cudagpu.cuda_device_context():
        #     print resultpc


e = Eval()
e.run()