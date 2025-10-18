describe('Telegram integration notice', () => {
  it('shows notification center trigger', () => {
    cy.visit('/');
    cy.contains('UGC Marketplace');
    cy.get('button[aria-label="Уведомления"]').should('be.visible');
  });
});
