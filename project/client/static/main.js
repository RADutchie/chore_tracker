// custom javascript

document.addEventListener("DOMContentLoaded", function() {
  const weekPicker = document.getElementById("weekPicker");
  const startOfWeekInput = document.getElementById("startOfWeek");
  const form = document.getElementById("queryForm");

  weekPicker.addEventListener("change", function() {
      let selectedDate = new Date(weekPicker.value);
      let day = selectedDate.getDay(); // 0 (Sunday) to 6 (Saturday)
      let difference = day === 0 ? -6 : 1 - day; // Adjust to Monday
      selectedDate.setDate(selectedDate.getDate() + difference);

      startOfWeekInput.value = selectedDate.toISOString().split("T")[0]; // Format as YYYY-MM-DD
      form.submit(); // Auto-submit form
  });
});

$( document ).ready(function() {
  console.log('Sanity Check!');
});