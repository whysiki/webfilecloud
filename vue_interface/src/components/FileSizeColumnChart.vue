<template>
  <div ref="chart" style="width: 100%; height: 400px"></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  props: {
    typesSizeCount: Object,
  },
  mounted() {
    this.initChart();
  },
  methods: {
    formatSize(size) {
      if (size < 1024) {
        return `${size} B`;
      } else if (size < 1024 * 1024) {
        return `${(size / 1024).toFixed(2)} KB`;
      } else if (size < 1024 * 1024 * 1024) {
        return `${(size / 1024 / 1024).toFixed(2)} MB`;
      } else {
        return `${(size / 1024 / 1024 / 1024).toFixed(2)} GB`;
      }
    },
    initChart() {
      const chart = echarts.init(this.$refs.chart);
      const option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        xAxis: {
          type: "category",
          data: Object.keys(this.typesSizeCount),
        },
        yAxis: {
          type: "value",
          axisLabel: {
            formatter: (value) => this.formatSize(value),
          },
          data: Object.values(this.typesSizeCount),
        },
        series: [
          {
            name: "File Size",
            type: "bar",
            data: Object.values(this.typesSizeCount),
            itemStyle: {
              color: (params) => {
                const colors = [
                  "#5470C6",
                  "#91CC75",
                  "#FAC858",
                  "#EE6666",
                  "#73C0DE",
                  "#3BA272",
                  "#FC8452",
                  "#9A60B4",
                  "#EA7CCC",
                ];
                return colors[params.dataIndex % colors.length];
              },
            },
          },
        ],
      };
      chart.setOption(option);
    },
  },
};
</script>

<style scoped></style>
