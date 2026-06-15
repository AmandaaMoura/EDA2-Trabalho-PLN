"""Fila implementada do zero."""


class Queue:
    """Fila simples com operações enqueue/dequeue."""

    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("A fila está vazia.")
        return self.items.pop(0)
