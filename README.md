
  async function copySelection() {
    if (!start.value || !end.value) return;

    const r1 = Math.min(start.value.row, end.value.row);
    const r2 = Math.max(start.value.row, end.value.row);

    const c1 = Math.min(start.value.col, end.value.col);
    const c2 = Math.max(start.value.col, end.value.col);

    const lines: string[] = [];

    for (let r = r1; r <= r2; r++) {
      const cols: string[] = [];

      for (let c = c1; c <= c2; c++) {
        cols.push(getCellValue(r, c));
      }

      lines.push(cols.join("\t"));
    }

    await navigator.clipboard.writeText(lines.join("\n"));
  }



const getCellValue = (rowIndex: number, colIndex: number): string => {
  const row = dataSource.value[rowIndex];

  if (!row) return "";

  // 고정 컬럼
  switch (colIndex) {
    case 0:
      return row.step ?? "";

    case 1:
      return row.eqp ?? "";

    case 2:
      return row.degree ?? "";
  }

  // 동적 컬럼
  const dynamicColumns = headerConfig.value.flatMap((group) => group.children);

  const column = dynamicColumns[colIndex - 3];

  if (!column) return "";

  return String(row[column.dataIndex] ?? "");
};
