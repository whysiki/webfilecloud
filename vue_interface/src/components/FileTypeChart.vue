<template>
  <div ref="chart" style="width: 100%; height: 400px"></div>
</template>

<script>
import * as echarts from "echarts";

export default {
  props: {
    typesCount: Object,
  },
  mounted() {
    this.initChart();
  },
  methods: {
    initChart() {
      const chart = echarts.init(this.$refs.chart);
      const option = {
        title: {
          text: "File Type Count",
        },
        tooltip: {},
        xAxis: {
          type: "category",
          data: Object.keys(this.typesCount),
        },
        yAxis: {
          type: "value",
        },
        series: [
          {
            type: "bar",
            data: Object.values(this.typesCount),
          },
        ],
      };
      chart.setOption(option);
    },
  },
};
</script>

<style scoped></style>
