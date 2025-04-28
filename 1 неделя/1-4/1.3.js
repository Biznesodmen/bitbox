let sum = 0;
const N = parseInt(prompt("Сколько чисел будем считать?")) || 0;
for (let i = 0; i < N; i++) {
  sum += parseFloat(prompt(`Введите число ${i+1}:`)) || 0;
}
alert(`Среднее: ${(sum/N).toFixed(2)}`);