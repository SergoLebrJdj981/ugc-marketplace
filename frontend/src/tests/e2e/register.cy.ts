describe('Registration flow', () => {
  it('registers a new brand user', () => {
    cy.visit('/register');
    cy.get('input[name="full_name"]').type('Test Brand');
    cy.get('input[name="email"]').type(`brand+${Date.now()}@example.com`);
    cy.get('input[name="password"]').type('Secret123!');
    cy.get('input[name="confirmPassword"]').type('Secret123!');
    cy.get('select[name="role"]').select('brand');
    cy.contains('Зарегистрироваться').click();
    cy.url().should('include', '/brand');
  });
});
