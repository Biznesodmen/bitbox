const distance1 = 180;  // Первое расстояние в км
const time1 = 2.5;      // Время в часах
const distance2 = 300;   // Второе расстояние в км

// Рассчитываем скорость (км/ч)
const speed = distance1 / time1; 

// Рассчитываем время для второго расстояния
const time2 = distance2 / speed;

// Разбиваем время на часы и минуты
const hours = Math.floor(time2);
const minutes = Math.round((time2 - hours) * 60);

// Выводим результаты
console.log(`Скорость автомобиля: ${speed} км/ч`);
console.log(`Время для ${distance2} км: ~${time2.toFixed(2)} часа (${hours} ч ${minutes} мин)`);