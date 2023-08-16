<template>
  <div class="column items-center q-my-lg loading-box">
    <q-spinner-hourglass class="q-mb-lg" color="primary" size="100px"/>
    <slot/>
  </div>
</template>

<style scoped lang="scss">
@import 'src/css/quasar.variables.scss';

.loading-box {
  background-color: #e3f2fd;
  border: 1px solid $primary;
  border-radius: 4px;
  padding: 16px;
}
</style>
