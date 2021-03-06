# ----------------------------------------------------------------------------
# Copyright 2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
from __future__ import division
from ngraph.op_graph.op_graph import TensorOp, make_axes, make_axis
import multiprocessing


def calculate_new_axes(axes, parallel_axis, num_devices, is_last):
    new_axes = list()
    for a in axes:
        if parallel_axis == a:
            remainder = a.length % num_devices
            new_length = a.length // num_devices
            if remainder > 0:
                if is_last:
                    new_length += remainder
            new_axis = make_axis(new_length, a.name)
            new_axes.append(new_axis)
        else:
            new_axes.append(a)
    new_axes = make_axes(new_axes)
    return new_axes


def get_slices(axes, parallel_axis, num_devices):
    new_slices = list()
    for i in range(num_devices):
        slices = list()
        for a in axes:
            s = slice(None)
            if parallel_axis == a:
                remainder = a.length % num_devices
                new_length = a.length // num_devices
                start = i * new_length
                stop = (i + 1) * new_length
                step = 1
                if remainder > 0:
                    if i == (num_devices - 1):
                        stop += remainder
                s = slice(start, stop, step)
            slices.append(s)
        new_slices.append(slices)
    return new_slices


class CommunicationOp(TensorOp):
    """
    Represents a communication op.

    Arguments:
        None
    """

    def __init__(self, node, args=None, axes=None, dtype=None):
        super(CommunicationOp, self).__init__(args=args, axes=axes, dtype=dtype)
        self.metadata['device'] = node.metadata['device']
        self.metadata['device_id'] = node.metadata['device_id']
        self.metadata['transformer'] = node.metadata['transformer']
        self.metadata['host_transformer'] = node.metadata['host_transformer']

    @property
    def is_communication_op(self):
        return True


class SendOp(CommunicationOp):
    """
    Represents a send op. Sets args, axes, dtype, and metadata.

    Arguments:
        from_node: The source node.
    """

    def __init__(self, from_node):
        super(SendOp, self).__init__(
            node=from_node,
            args=tuple([from_node]),
            axes=from_node.axes,
            dtype=from_node.dtype)


class RecvOp(CommunicationOp):
    """
    Represents a recv op. Sets args, axes, dtype, and metadata.

    Arguments:
        to_node: The destination node.
        send_node: The send node associated with this recv node.
    """

    def __init__(self, to_node, send_node):
        super(RecvOp, self).__init__(
            node=to_node,
            args=(),
            axes=to_node.axes,
            dtype=to_node.dtype)
        self._send_node = send_node

    def send_node(self):
        return self._send_node


class ScatterSendOp(SendOp):
    """
    Represents a scatter send op. Sets destination device ids and slices.

    Arguments:
        from_node: The source node.
        to_node: The destination node.
    """

    def __init__(self, from_node, to_node):
        super(ScatterSendOp, self).__init__(from_node)
        self.to_id = to_node.metadata['device_id']
        self.slices = get_slices(self.axes,
                                 to_node.metadata['parallel'],
                                 len(self.to_id))


class ScatterRecvOp(RecvOp):
    """
    Represents a scatter recv op.

    Arguments:
        to_node: The destination node.
        send_node: The scatter send node associated with this node.
    """

    def __init__(self, to_node, send_node):
        super(ScatterRecvOp, self).__init__(to_node, send_node)


class GatherSendOp(SendOp):
    """
    Represents a gather send op.

    Arguments:
        from_node: The source node.
    """

    def __init__(self, from_node):
        super(GatherSendOp, self).__init__(from_node)


class GatherRecvOp(RecvOp):
    """
    Represents a gather recv op. Sets metadata, source device ids and
    slices.

    Arguments:
        from_node: The source node.
        to_node: The destination node.
        send_node: The gather send node associated with this node.
    """

    def __init__(self, from_node, to_node, send_node):
        super(GatherRecvOp, self).__init__(to_node, send_node)
        self.metadata['marker'] = 'gather'
        self.metadata['parallel'] = from_node.metadata['parallel']
        self.from_id = from_node.metadata['device_id']
        self.slices = get_slices(self.axes,
                                 self.metadata['parallel'],
                                 len(self.from_id))


class GpuQueueSendOp(SendOp):

    def __init__(self, from_node):
        super(GpuQueueSendOp, self).__init__(from_node)
        self.queue = multiprocessing.Queue()


class GpuQueueRecvOp(RecvOp):

    def __init__(self, to_node, send_node):
        super(GpuQueueRecvOp, self).__init__(to_node, send_node)
        self.queue = send_node.queue


class NumpyQueueSendOp(SendOp):

    def __init__(self, from_node):
        super(NumpyQueueSendOp, self).__init__(from_node)
        self.queue = multiprocessing.Queue()


class NumpyQueueRecvOp(RecvOp):

    def __init__(self, to_node, send_node):
        super(NumpyQueueRecvOp, self).__init__(to_node, send_node)
        self.queue = send_node.queue


class NumpyQueueScatterSendOp(ScatterSendOp):

    def __init__(self, from_node, to_node):
        super(NumpyQueueScatterSendOp, self).__init__(from_node, to_node)
        self.shared_queues = list()
        for i in range(len(to_node.metadata['device_id'])):
            self.shared_queues.append(multiprocessing.Queue())
        self.comm_type = 'queue'


class NumpyQueueScatterRecvOp(ScatterRecvOp):

    def __init__(self, to_node, send_node, device_idx=None):
        super(NumpyQueueScatterRecvOp, self).__init__(to_node, send_node)
        if device_idx:
            self.idx = device_idx
        else:
            self.idx = 0
        self.shared_queues = send_node.shared_queues


class NumpyQueueGatherSendOp(GatherSendOp):

    def __init__(self, from_node, clone_node=None, device_idx=None):
        super(NumpyQueueGatherSendOp, self).__init__(from_node)
        self.shared_queues = list()
        if clone_node:
            self.idx = device_idx
            self.shared_queues = clone_node.shared_queues
        else:
            self.idx = 0
            for i in range(len(from_node.metadata['device_id'])):
                self.shared_queues.append(multiprocessing.Queue())


class NumpyQueueGatherRecvOp(GatherRecvOp):

    def __init__(self, from_node, to_node, send_node):
        super(NumpyQueueGatherRecvOp, self).__init__(from_node, to_node, send_node)
        self.shared_queues = send_node.shared_queues
