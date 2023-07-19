<template>
  <q-page class="q-px-lg q-mx-auto" style="max-width: 1000px;">
    <h3>Tango Statistics</h3>
    <div class="button-row q-mb-lg">
      <q-btn icon="west" label="Back to portal home" color="primary" to="/"/>
      <q-btn icon="refresh" label="Refresh" color="primary" @click="updateTangoStats"/>
      <q-btn icon="visibility" label="Toggle Alternative View" color="primary"
             @click="state.alternativeView = !state.alternativeView"/>
    </div>

    <div v-if="state.loading">
      <FullWidthLoading>
        Loading Tango statistics...
      </FullWidthLoading>
    </div>
    <div v-else-if="state.error">
      <p>Error: {{ state.message }}</p>
      <p v-if="state.success">(Showing previously fetched data below)</p>
    </div>
    <template v-if="state.success">
      <template v-if="state.alternativeView">
        <div class="row">
          <div>
            <div class="timeframe histogram-entry">
              <p><b>Timeframe</b></p>
            </div>
          </div>
          <div class="col-grow">
            <div class="histogram-entry">
              <p><b>Submissions within timeframe</b></p>
            </div>
          </div>
        </div>
        <div class="row" v-for="point in state.data" :key="point.seconds">
          <div>
            <div class="timeframe histogram-entry">
              <p>{{ point.timeframe }}</p>
            </div>
          </div>
          <div class="col-grow">
            <div class="histogram-entry alt">
              <div class="bar flex" :style="{width: `${point.percent}%`}">
                <p style="text-align: right; width: 100%; margin-right: 6px;">{{ point.count }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <div v-for="point in state.data" :key="point.seconds">
          <div class="histogram-entry">
            <div class="bar" :style="{width: `${point.percent}%`}"/>
            <p>{{ point.sentence }}</p>
          </div>
        </div>
      </template>
    </template>

    <div style="height: 100px;"></div>
  </q-page>
</template>

<script setup lang="ts">
import {reactive} from 'vue';
import {TangoHistogramPoint} from "src/types/TangoHistogramPoint";
import FullWidthLoading from "components/FullWidthLoading.vue";


const state = reactive({
  loading: false,
  error: false, // This will be true if the last refresh request failed
  success: false, // This will remain true once there is data, even if a later refresh request fails
  message: '', // Use to show errors
  data: null as TangoHistogramPoint[] | null,
  alternativeView: false,
})

function updateTangoStats() {
  state.loading = true
  fetch('/portal/api/tango-stats/', {}).then(resp => resp.json())
    .then(data => {
      if (data.success) {
        state.error = false
        state.success = true
        state.data = data.data
      } else {
        state.error = true
        state.message = data.error
      }
    })
    .finally(() => {
      state.loading = false
    })
}

updateTangoStats()
</script>

<style scoped lang="scss">
@import 'src/css/quasar.variables.scss';

.histogram-entry {
  position: relative;
  margin-bottom: 2px;
  height: 30px;
}

.histogram-entry p {
  padding: 4px;
  margin: 0 0 0 6px;
}

.histogram-entry > * {
  position: absolute;
  top: 0;
  height: 100%;
}

.histogram-entry .bar {
  background-color: #8fb7ff;
  border-radius: 10px;
}

.timeframe {
  width: 140px;
  text-align: right;
}

</style>
