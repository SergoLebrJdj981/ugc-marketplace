describe('UX Flow', () => {
  const brandEmail = 'slebronov@mail.ru';
  const brandPassword = '12322828';

  it('logs in, navigates dashboard, toggles theme and logs out', () => {
    cy.visit('/');

    cy.contains('button', 'Войти как бренда').click();
    cy.contains('button[type="submit"]', 'Войти').click();

    cy.url({ timeout: 10000 }).should('include', '/brand');

    cy.contains('button', 'Светлая тема').click();
    cy.contains('button', 'Тёмная тема');
    cy.reload();
    cy.contains('button', 'Тёмная тема');

    cy.contains('button', 'Выйти').click({ force: true });
    cy.url({ timeout: 10000 }).should('eq', 'http://localhost:3000/');
  });
});
