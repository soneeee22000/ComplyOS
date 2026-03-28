"use client";

import { Document, Page, Text, View, StyleSheet } from "@react-pdf/renderer";

const BLUE = "#1e40af";
const DARK = "#0f172a";
const SLATE = "#334155";
const MUTED = "#64748b";
const BORDER = "#e2e8f0";
const LIGHT_BG = "#f8fafc";

const styles = StyleSheet.create({
  page: {
    padding: 50,
    paddingTop: 80,
    paddingBottom: 60,
    fontFamily: "Helvetica",
    fontSize: 10,
    color: DARK,
  },
  headerBar: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: 4,
    backgroundColor: BLUE,
  },
  headerArea: {
    position: "absolute",
    top: 15,
    left: 50,
    right: 50,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  logo: {
    fontSize: 14,
    fontFamily: "Helvetica-Bold",
    color: BLUE,
  },
  headerMeta: {
    fontSize: 8,
    color: MUTED,
    textAlign: "right",
  },
  h1: {
    fontSize: 22,
    fontFamily: "Helvetica-Bold",
    color: BLUE,
    marginBottom: 12,
    marginTop: 20,
  },
  h2: {
    fontSize: 16,
    fontFamily: "Helvetica-Bold",
    color: BLUE,
    marginBottom: 8,
    marginTop: 16,
    paddingBottom: 4,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  h3: {
    fontSize: 12,
    fontFamily: "Helvetica-Bold",
    color: DARK,
    marginBottom: 6,
    marginTop: 12,
  },
  paragraph: {
    fontSize: 10,
    lineHeight: 1.6,
    marginBottom: 8,
    color: SLATE,
  },
  bulletItem: {
    flexDirection: "row",
    marginBottom: 4,
    paddingLeft: 12,
  },
  bullet: {
    width: 14,
    fontSize: 10,
    color: BLUE,
    fontFamily: "Helvetica-Bold",
  },
  bulletText: {
    flex: 1,
    fontSize: 10,
    lineHeight: 1.5,
    color: SLATE,
  },
  tableRow: {
    flexDirection: "row",
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  tableHeader: {
    flexDirection: "row",
    backgroundColor: BLUE,
  },
  tableHeaderCell: {
    flex: 1,
    padding: 6,
    fontSize: 8,
    fontFamily: "Helvetica-Bold",
    color: "#ffffff",
    textTransform: "uppercase",
  },
  tableCell: {
    flex: 1,
    padding: 6,
    fontSize: 9,
    color: SLATE,
  },
  tableCellEven: {
    flex: 1,
    padding: 6,
    fontSize: 9,
    color: SLATE,
    backgroundColor: LIGHT_BG,
  },
  codeBlock: {
    backgroundColor: "#1e293b",
    color: "#e2e8f0",
    padding: 10,
    borderRadius: 4,
    marginBottom: 8,
    fontFamily: "Courier",
    fontSize: 8,
  },
  separator: {
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
    marginVertical: 12,
  },
  footer: {
    position: "absolute",
    bottom: 25,
    left: 50,
    right: 50,
    flexDirection: "row",
    justifyContent: "space-between",
    fontSize: 8,
    color: MUTED,
  },
  pageNumber: {
    fontSize: 8,
    color: MUTED,
  },
});

function parseMarkdownToPdfElements(content: string) {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeBuffer: string[] = [];
  let inTable = false;
  let tableRows: string[][] = [];
  let isFirstTableRow = true;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("```")) {
      if (inCodeBlock) {
        elements.push(
          <View key={`code-${i}`} style={styles.codeBlock}>
            <Text>{codeBuffer.join("\n")}</Text>
          </View>,
        );
        codeBuffer = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      continue;
    }

    if (line.startsWith("|") && line.includes("|")) {
      if (line.replace(/[|\-\s]/g, "").length === 0) continue;

      const cells = line
        .split("|")
        .filter((c) => c.trim())
        .map((c) => c.trim());

      if (!inTable) {
        inTable = true;
        isFirstTableRow = true;
        tableRows = [cells];
      } else {
        tableRows.push(cells);
      }
      continue;
    }

    if (inTable) {
      tableRows.forEach((row, rowIdx) => {
        const isHeader = rowIdx === 0 && isFirstTableRow;
        elements.push(
          <View
            key={`table-${i}-${rowIdx}`}
            style={isHeader ? styles.tableHeader : styles.tableRow}
          >
            {row.map((cell, cellIdx) => (
              <Text
                key={cellIdx}
                style={
                  isHeader
                    ? styles.tableHeaderCell
                    : rowIdx % 2 === 0
                      ? styles.tableCellEven
                      : styles.tableCell
                }
              >
                {cell}
              </Text>
            ))}
          </View>,
        );
      });
      inTable = false;
      tableRows = [];
      isFirstTableRow = true;
    }

    if (line.startsWith("### ")) {
      elements.push(
        <Text key={`h3-${i}`} style={styles.h3}>
          {line.replace("### ", "")}
        </Text>,
      );
    } else if (line.startsWith("## ")) {
      elements.push(
        <Text key={`h2-${i}`} style={styles.h2}>
          {line.replace("## ", "")}
        </Text>,
      );
    } else if (line.startsWith("# ")) {
      elements.push(
        <Text key={`h1-${i}`} style={styles.h1}>
          {line.replace("# ", "")}
        </Text>,
      );
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <View key={`bullet-${i}`} style={styles.bulletItem}>
          <Text style={styles.bullet}>&#8226;</Text>
          <Text style={styles.bulletText}>{line.replace(/^[-*]\s/, "")}</Text>
        </View>,
      );
    } else if (line.startsWith("---") || line.startsWith("***")) {
      elements.push(<View key={`sep-${i}`} style={styles.separator} />);
    } else if (line.trim()) {
      const cleanLine = line
        .replace(/\*\*(.*?)\*\*/g, "$1")
        .replace(/\*(.*?)\*/g, "$1")
        .replace(/`(.*?)`/g, "$1");
      elements.push(
        <Text key={`p-${i}`} style={styles.paragraph}>
          {cleanLine}
        </Text>,
      );
    }
  }

  if (inTable && tableRows.length > 0) {
    tableRows.forEach((row, rowIdx) => {
      elements.push(
        <View
          key={`table-end-${rowIdx}`}
          style={rowIdx === 0 ? styles.tableHeader : styles.tableRow}
        >
          {row.map((cell, cellIdx) => (
            <Text
              key={cellIdx}
              style={rowIdx === 0 ? styles.tableHeaderCell : styles.tableCell}
            >
              {cell}
            </Text>
          ))}
        </View>,
      );
    });
  }

  return elements;
}

interface CompliancePDFDocumentProps {
  content: string;
  systemName: string;
  docType: string;
  generatedAt: string;
}

export function CompliancePDFDocument({
  content,
  systemName,
  docType,
  generatedAt,
}: CompliancePDFDocumentProps) {
  const date = new Date(generatedAt).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        <View style={styles.headerBar} fixed />
        <View style={styles.headerArea} fixed>
          <Text style={styles.logo}>ComplyOS</Text>
          <View>
            <Text style={styles.headerMeta}>{systemName}</Text>
            <Text style={styles.headerMeta}>
              {docType
                .replace(/_/g, " ")
                .replace(/\b\w/g, (c) => c.toUpperCase())}
            </Text>
            <Text style={styles.headerMeta}>{date}</Text>
          </View>
        </View>
        {parseMarkdownToPdfElements(content)}
        <View style={styles.footer} fixed>
          <Text>Generated by ComplyOS - EU AI Act Compliance Agent</Text>
          <Text
            render={({ pageNumber, totalPages }) =>
              `Page ${pageNumber} of ${totalPages}`
            }
            style={styles.pageNumber}
          />
        </View>
      </Page>
    </Document>
  );
}
