class Filepath:
    def __init__(self):
        self.type = {}

        self.datasetPath = "../Dataset/"

        self.sourcePath = self.datasetPath + "src/"
        self.sourceType = "source"
        self.type["src"] = self.datasetPath + "src/"
        self.srcDump = self.datasetPath + "src-dump/"
        self.srcDump2 = self.datasetPath + "src-dump2/"

        self.suspiciousPath = self. datasetPath + "susp/"
        self.suspiciousType = "suspicious"
        self.type["susp"] = self. datasetPath + "susp/"
        self.suspDump = self.datasetPath + "susp-dump/"
        self.suspDump2 = self.datasetPath + "susp-dump2/"

        self.noPlagiarismPath = self.datasetPath + "01-no-plagiarism/"
        self.noPlagiarismType = "no-plagiarism"

        self.noObfuscationPath = self.datasetPath + "02-no-obfuscation/"
        self.noObfuscationType = "no-obfuscation"

        self.randomObfuscationPath = self.datasetPath + "03-random-obfuscation/"
        self.randomObfuscationType = "random-obfuscation"

        self.translationObfuscationPath = self.datasetPath + "04-translation-obfuscation/"
        self.translationObfuscationType = "translation-obfuscation"

        self.summaryObfuscationPath = self.datasetPath + "05-summary-obfuscation/"
        self.summaryObfuscationType = "summary-obfuscation"

        self.pairs = self.datasetPath + "pairs"

        self.pairsNoPlag = self.noPlagiarismPath + "new"
        self.pairsNoObs = self.noObfuscationPath + "new"
        self.pairsRandomObs = self.randomObfuscationPath + "new"
        self.pairsTransObs = self.translationObfuscationPath + "new"
        self.pairsSummaryObs = self.summaryObfuscationPath + "new"