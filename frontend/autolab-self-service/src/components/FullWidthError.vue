<template>
  <div class="column items-center q-my-lg error-box">
    <q-icon class="q-mb-lg" name="error" color="negative" size="100px"/>
    <slot/>
  </div>
</template>

<style scoped lang="scss">
@import 'src/css/quasar.variables.scss';

.error-box {
  background-color: #ffebee;
  border: 1px solid $negative;
  border-radius: 4px;
  padding: 16px;
}
</style>
