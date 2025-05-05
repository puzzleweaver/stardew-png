
class Prints:
    
    def columns(columns):
        out = ""

        maxRowLens = [0 for column in columns]
        maxLines = 0
        for i in range(len(columns)):
            lines = columns[i].split("\n")
            maxLines = max(maxLines, len(lines))
            for line in lines:
                maxRowLens[i] = max(maxRowLens[i], len(line))

        # spacer = "| " + " | ".join([" "*maxRowLen for maxRowLen in maxRowLens]) + " |"
        bumper = "+-" + "-+-".join(["-"*maxRowLen for maxRowLen in maxRowLens]) + "-+"
        rows = []
        def getRow(j):
            row = []
            for i in range(len(columns)):
                lines = columns[i].split("\n")
                line = ""
                if j < len(lines):
                    line = lines[j]
                row.append(line.ljust(maxRowLens[i]))
            return row
        for j in range(maxLines):
            row = "| " + " | ".join(getRow(j)) + " |"
            rows.append(row)
        return "\n".join([ bumper ] + rows + [ bumper ])