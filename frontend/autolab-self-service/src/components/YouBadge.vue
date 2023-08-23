<template>
  <span class="you-badge q-ml-sm"><slot>You</slot></span>
</template>

<style scoped lang="scss">
@import "../css/quasar.variables";

.you-badge {
  background-color: $primary;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
