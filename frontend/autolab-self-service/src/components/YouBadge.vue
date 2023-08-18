<template>
  <span class="you-badge"><slot>You</slot></span>
</template>

<style scoped lang="scss">
@import "../css/quasar.variables";

.you-badge {
  background-color: $primary;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 12px;
}
</style>
