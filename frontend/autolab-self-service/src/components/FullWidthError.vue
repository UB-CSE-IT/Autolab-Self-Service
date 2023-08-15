<template>
  <div class="column items-center q-ma-lg error-box">
    <q-icon class="q-mb-lg" name="error" color="negative" size="100px"/>
    <slot/>
  </div>
</template>

<style scoped>
.error-box {
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  padding: 16px;
}
</style>
