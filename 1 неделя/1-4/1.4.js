class User {
    constructor(login, password, email) {
      this.login = login;
      this.password = password;
      this.email = email;
      this.permissions = [];
    }
    checkCredentials(inputLogin, inputPassword) {
      if (this.login !== inputLogin) return "Неверный логин!";
      if (this.password !== inputPassword) return "Неверный пароль!";
      return `Добро пожаловать, ${this.login}!`;
    }
  }
  class Admin extends User {
    constructor(login, password, email, accessLevel = 2) {
      super(login, password, email);
      this.accessLevel = accessLevel;
      this.isAdmin = true;
    }
    grantPermissions(user, permissions) {
      if (!this.isAdmin) return "Только админ может выдавать права!";
      user.permissions = [...new Set([...user.permissions, ...permissions])];
      return `[Админ ${this.login}] выдал права ${user.login}: ${permissions.join(', ')}`;
    }
  }
  class UserManager {
    constructor() {
      this.users = [];
    }
    register(login, password, email, isAdmin = false) {
      if (this.users.some(u => u.login === login)) {
        return `Ошибка: логин ${login} уже занят!`;
      }
      const newUser = isAdmin 
        ? new Admin(login, password, email)
        : new User(login, password, email);
      this.users.push(newUser);
      return `${isAdmin ? 'Администратор' : 'Пользователь'} ${login} зарегистрирован!`;
    }
    makeMariaAdmin() {
      const maria = this.users.find(u => u.login === 'Мария');
      if (!maria) {
        this.register('Мария', 'superpass', 'maria@example.com', true);
        return "Мария зарегистрирована как администратор!";
      }
      if (!maria.isAdmin) {
        const adminMaria = new Admin(maria.login, maria.password, maria.email);
        this.users = this.users.map(u => u.login === 'Мария' ? adminMaria : u);
        return "Мария теперь администратор!";
      }
      return "Мария уже администратор!";
    }
  }
  const manager = new UserManager();
  console.log(manager.register('Павел', 'qwerty123', 'pavel@mail.ru'));
  console.log(manager.register('Мария', 'password', 'maria@example.com'));
  console.log("\n" + manager.makeMariaAdmin());
  const maria = manager.users.find(u => u.login === 'Мария');
  if (maria && maria.isAdmin) {
    console.log(maria.grantPermissions(
      manager.users.find(u => u.login === 'Павел'), 
      ['delete', 'ban']
    ));
  }
  console.log("\nСтатистика:");
  console.log(`Администраторов: ${manager.users.filter(u => u.isAdmin).length}`);
  console.log(`Права Павла: ${
    manager.users.find(u => u.login === 'Павел')?.permissions.join(', ') || 'нет'
  }`);
  