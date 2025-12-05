from dataclasses import dataclass
import matplotlib.pyplot as plt


@dataclass
class PlotRecord:
    maxFitness: int
    qdScore: float
    coverage: int


class MapElitesPlotter:
    def __init__(self, plotFilepath: str):
        self.records: list[PlotRecord] = []
        self.plotFilepath = plotFilepath

    def addRecord(self, record: PlotRecord):
        self.records.append(record)

    def plotMaxFitnessAndQDScore(self):
        iterations = list(range(len(self.records)))
        plt.figure(figsize=(10, 6))

        plt.plot(iterations, [x.maxFitness for x in self.records], label="Max Fitness")
        plt.plot(iterations, [x.qdScore for x in self.records], label="QD-Score")

        plt.xlabel("Iteration")
        plt.ylabel("Value")
        plt.title("Map-Elites Training Progress")
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(self.plotFilepath + "_Fitness.png", dpi=300)

    def plotCoverage(self):
        iterations = list(range(len(self.records)))
        plt.figure(figsize=(10, 6))

        plt.plot(iterations, [x.coverage for x in self.records], label="Coverage")

        plt.xlabel("Iteration")
        plt.ylabel("Value")
        plt.title("Map-Elites Training Progress")
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(self.plotFilepath + "_Coverage.png", dpi=300)
