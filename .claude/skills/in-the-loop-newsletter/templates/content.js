/**
 * Copy to work/content.js and edit. This describes the issue for the accessible
 * Word build; build_docx.js turns it into real heading styles, alt text and
 * live links so the content file does not have to.
 *
 * Keep the wording identical to the PDF. The two files are emailed together and
 * are read as one thing.
 *
 * Block types:
 *   { type: 'h2',      text }
 *   { type: 'p',       text, bold? }
 *   { type: 'bullets', items: [] }
 *   { type: 'callout', text: '' | [], colour: 'navy'|'blue'|'green'|'orange' }
 *   { type: 'link',    before?, text, href, after? }
 *   { type: 'contact', name, role, phone, email }
 *   { type: 'image',   file, width, height, name, description, caption? }
 *
 * On images: `description` is the alt text a screen reader reads aloud, so
 * describe what is shown and why it is there. `caption` is visible text under
 * the image — sighted readers of this version get the illustration described
 * too, which is the point of the accessible edition.
 */
module.exports = {
  title: 'In The Loop',
  issue: 'Issue 00  |  Month 2026',
  strapline: 'A monthly update for CoreEd learners.',
  description: 'Accessible version of the In The Loop learner newsletter.',

  sections: [
    {
      heading: 'Welcome',
      blocks: [
        { type: 'p', text: 'Opening paragraph.' },
        {
          type: 'link',
          before: 'Questions, or something you would like covered next time? Email ',
          text: 'enquiries@CoreEd.co.uk',
          href: 'mailto:enquiries@CoreEd.co.uk',
          after: '.',
        },
        {
          type: 'image',
          file: 'characters/Corrie_Happy.png',
          width: 62, height: 93,
          name: 'Corrie, apprentice',
          description: 'Illustration of Corrie, a CoreEd apprentice in a blue hoodie, smiling.',
          caption: 'Illustration: Corrie, one of our apprentices.',
        },
      ],
    },
    {
      heading: '1. Section heading',
      blocks: [
        { type: 'p', text: 'Body copy.' },
        { type: 'h2', text: 'A sub-heading' },
        { type: 'bullets', items: ['First point', 'Second point'] },
        {
          type: 'callout',
          colour: 'orange',
          text: 'A short highlighted note.',
        },
      ],
    },
    {
      heading: '2. We are here to help',
      blocks: [
        {
          type: 'contact',
          name: 'Jeannette Adrian',
          role: 'Designated Safeguarding Lead and Wellbeing Support',
          phone: '07557 093701',
          email: 'jeannette@CoreEd.co.uk',
        },
        {
          type: 'contact',
          name: 'Airam Neesa',
          role: 'Deputy Designated Safeguarding Lead',
          phone: '07912 342 367',
          email: 'airam@CoreEd.co.uk',
        },
        { type: 'h2', text: 'General enquiries' },
        {
          type: 'link',
          before: 'Email ',
          text: 'enquiries@CoreEd.co.uk',
          href: 'mailto:enquiries@CoreEd.co.uk',
          after: '  |  The Media Centre, 7 Northumberland Street, Huddersfield, HD1 1RL',
        },
        { type: 'p', text: 'In an emergency, always call 999.', bold: true },
      ],
    },
  ],

  signoff: {
    who: 'The CoreEd Team',
    text: 'Closing line.',
  },
};
