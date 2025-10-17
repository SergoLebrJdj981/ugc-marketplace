describe('Login flow', () => {
  it('allows login via home buttons', () => {
    cy.visit('/');
    cy.contains('Войти как').first().click();
    cy.get('input[type="email"]').clear().type('slebronov@mail.ru');
    cy.get('input[type="password"]').clear().type('12322828');
    cy.contains('Войти').click();
    cy.url().should('include', '/brand');
  });
});
