function gradeCalculator(score) {
    if (score >= 90 && score <= 100) {
        return "A";
    } else if (score >= 75 && score <= 89) {
        return "B";
    } else if (score >= 60 && score <= 74) {
        return "C";
    } else if (score >= 0 && score < 60) {
        return "F";
    } else {
        return "Ошибка: введите число от 0 до 100";
    }
}

const score = 85;
console.log(`Оценка: ${gradeCalculator(score)}`);