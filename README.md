watch(rulerMode, (isOn: boolean) => {
  const graph = getGraph() as any;
  if (!graph?._context) return;
  graph._context.scrollZoom = isOn ? false : plotConfig.scrollZoom ?? true;
});
