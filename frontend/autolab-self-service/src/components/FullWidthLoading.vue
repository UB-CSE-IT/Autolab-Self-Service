<template>
  <div class="column items-center q-ma-lg loading-box">
    <q-spinner-hourglass class="q-mb-lg" color="primary" size="100px"/>
    <slot/>
  </div>
</template>

<style scoped>
.loading-box {
  background-color: #e3f2fd;
  border: 1px solid #bbdefb;
  border-radius: 4px;
  padding: 16px;
}
</style>
