<template>
  <div class="navigation-bar" title="Current path">
    <div class="navigation-bar__path">
      <span>{{ pathstr }}</span>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      pathstr: "/",
    };
  },
  mounted() {
    this.emitter.on("update-current-nodes", (value) => {
      this.pathstr = "/" + JSON.parse(value).join("/");
    });
  },
};
</script>

<style scoped>
.navigation-bar {
  box-shadow: 0 0 10px rgba(176, 43, 43, 0.1);
  border-radius: 10px;
  align-items: center;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.5);
  margin: 20px 0;
}

.navigation-bar__path {
  display: flex;
  flex-wrap: wrap;
}

.navigation-bar__path span {
  font-weight: bold;
  background-color: #16723c;
  border-radius: 10px;
  box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.5);
  padding: 5px 10px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.navigation-bar__path span:hover {
  background-color: #16723c;
}
</style>
