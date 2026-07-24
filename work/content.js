/**
 * Accessible Word version of In The Loop, August 2026 (learner edition).
 * Wording is kept identical to work/issue.html — the two files are emailed
 * together and read as one thing. build_docx.js turns this into real heading
 * styles, alt text and live links.
 */
module.exports = {
  title: 'In The Loop',
  issue: 'Learner edition  |  August 2026',
  strapline: 'Your monthly update from CoreEd. News, dates and support for apprentices.',
  description: 'Accessible version of the In The Loop learner newsletter, August 2026.',

  sections: [
    {
      heading: 'Welcome',
      blocks: [
        {
          type: 'p',
          text: 'Welcome to the August issue. This is a quieter month for a lot of us, with some teams on leave and workshops running a reduced timetable, so this issue is about keeping your training on track over the summer and knowing where to turn if you need support.',
        },
        {
          type: 'link',
          before: 'Inside you will find this month’s inclusion date, a reminder about English and maths as results season arrives, the dates worth putting in your diary, and how to reach the safeguarding team. If there is something you would like us to cover next time, email ',
          text: 'enquiries@CoreEd.co.uk',
          href: 'mailto:enquiries@CoreEd.co.uk',
          after: '.',
        },
        {
          type: 'image',
          file: 'characters/Corrie_Happy.png',
          width: 62, height: 93,
          name: 'Corrie Patel, apprentice',
          description: 'Illustration of Corrie Patel, a CoreEd apprentice, smiling and giving a thumbs up.',
          caption: 'Illustration: Corrie Patel, one of our apprentices.',
        },
      ],
    },
    {
      heading: '1. Celebrating our results',
      blocks: [
        {
          type: 'p',
          text: 'We want to mark what this cohort has achieved this quarter. The figures below are being confirmed with our quality team and will be filled in before this issue goes out.',
        },
        { type: 'bullets', items: [
          '[XX%] of apprentices passed their end-point assessment this quarter.',
          '[XX%] achieved a distinction or merit.',
          '[XX] learners completed their apprenticeship.',
        ]},
        {
          type: 'callout',
          colour: 'blue',
          text: 'Every one of those results is a piece of work fitted around a job and, for many of you, a household. If you have finished this summer, well done, and do keep your certificate somewhere safe. If you are still going, the same steady effort is what gets you there.',
        },
        {
          type: 'p',
          bold: true,
          text: 'Internal note, remove before sending: the three figures above are placeholders. Ask the quality team for this quarter’s confirmed pass rate, distinction and merit rate, and completion count. Do not send with any figure showing.',
        },
      ],
    },
    {
      heading: '2. Inclusion this month',
      blocks: [
        {
          type: 'p',
          text: 'International Youth Day falls on Wednesday 12 August. It is a United Nations day that recognises the part young people play in their communities and at work. This year’s theme is “Different Contexts, Common Aspirations”, a reminder that although our circumstances differ, what we want from work and study is often the same: to be respected, to keep learning, and to get on.',
        },
        {
          type: 'p',
          text: 'As an apprentice you are part of that. If there is something about your training that would work better for you, whether that is how sessions are timed or how feedback reaches you, tell your coach. Small changes are easier to make than you might think, and the earlier you raise them the more we can do.',
        },
        {
          type: 'callout',
          colour: 'blue',
          text: 'Mark the day: Wednesday 12 August 2026. If your workplace runs a staff network or a wellbeing group, it is a good week to ask what they have planned, or to suggest something yourself.',
        },
        {
          type: 'image',
          file: 'characters/Ben_Encouraging.png',
          width: 60, height: 107,
          name: 'Ben Carter, mentor',
          description: 'Illustration of Ben Carter, a CoreEd mentor, smiling with an encouraging, open-handed gesture.',
          caption: 'Illustration: Ben Carter, one of our mentors.',
        },
      ],
    },
    {
      heading: '3. Functional Skills: English and maths',
      blocks: [
        {
          type: 'p',
          text: 'August is results season. A-level results are published on Thursday 13 August and GCSE results on Thursday 20 August. If you are waiting on a grade that changes what you need to do for Functional Skills, talk to your coach as soon as you have it.',
        },
        {
          type: 'p',
          text: 'Whether you need to complete Functional Skills English and maths depends on your age and the type of apprenticeship you are on, and the rules have changed in recent years. Please do not assume you are exempt. Check with your coach, who can confirm what applies to you and book any exams you still have left.',
        },
        { type: 'h2', text: 'If you have exams to sit' },
        { type: 'bullets', items: [
          'Book early. Summer sittings fill up.',
          'Ask your coach for a past paper to practise with.',
          'Tell us if you need a quiet room or extra time.',
        ]},
        { type: 'h2', text: 'If you are not sure' },
        { type: 'bullets', items: [
          'Do not guess your status from a friend’s.',
          'One message to your coach settles it.',
          'We would rather check twice than miss a deadline.',
        ]},
        {
          type: 'image',
          file: 'characters/Priya_Supportive.png',
          width: 62, height: 95,
          name: 'Priya Shah, assessor',
          description: 'Illustration of Priya Shah, a CoreEd assessor, standing with a warm, supportive expression.',
          caption: 'Illustration: Priya Shah, one of our assessors.',
        },
      ],
    },
    {
      heading: '4. Dates for your diary',
      blocks: [
        { type: 'bullets', items: [
          'Wednesday 12 August: International Youth Day.',
          'Thursday 13 August: A-level results day.',
          'Wednesday 19 August: World Humanitarian Day.',
          'Thursday 20 August: GCSE results day.',
          'Into September: coach and workshop timetables change over the summer. Check your calendar, or ask your coach for the term dates once term restarts.',
        ]},
      ],
    },
    {
      heading: '5. Safeguarding team update',
      blocks: [
        {
          type: 'p',
          text: 'The summer can be a harder stretch than it looks. Routines change, money is often tighter, and it is easier to feel out of touch when workshops are quieter. If something is worrying you, at work or outside it, tell us the same day. Early concerns are easier to resolve.',
        },
        {
          type: 'p',
          text: 'We will listen, agree what happens next with you, and keep you informed. Raising a concern does not put your apprenticeship at risk. The safeguarding team’s contact details are below.',
        },
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
        { type: 'h2', text: 'How to raise a concern' },
        { type: 'bullets', items: [
          'Tell us the same day, by phone, email or in person.',
          'Say what has happened and what you are worried about.',
          'We agree the next step with you before we take it.',
        ]},
        { type: 'h2', text: 'Worried about someone else?' },
        { type: 'bullets', items: [
          'You do not need to be certain to speak up.',
          'Pass on what you have noticed to the team.',
          'We will take it from there and keep it discreet.',
        ]},
        {
          type: 'callout',
          colour: 'orange',
          text: 'Prevent. CoreEd has a duty under the government’s Prevent programme to help keep people safe from being drawn into extremism. If you are worried that you, or someone you know, is being pulled towards extreme views or violence, tell the safeguarding team. We would rather you raised it and were wrong than said nothing. In an emergency, always call 999.',
        },
        {
          type: 'image',
          file: 'characters/Mascot_Safety_Tip.png',
          width: 92, height: 70,
          name: 'CoreEd Safety Guardian mascot',
          description: 'Illustration of the CoreEd Safety Guardian, a friendly shield-shaped mascot, offering a safety tip.',
          caption: 'Illustration: the CoreEd Safety Guardian.',
        },
      ],
    },
    {
      heading: '6. Support and resources',
      blocks: [
        {
          type: 'p',
          text: 'If you are struggling this summer, you do not have to wait for a session to talk to someone. These services are free and you can use them yourself, at any time.',
        },
        { type: 'h2', text: 'Someone to talk to' },
        { type: 'bullets', items: [
          'Samaritans. Call 116 123, free, day or night.',
          'Shout. Text the word SHOUT to 85258, free, 24 hours.',
        ]},
        { type: 'h2', text: 'If you need health help' },
        { type: 'bullets', items: [
          'NHS 111. Call 111 and choose the mental health option.',
          'Your GP. Still the best route for anything ongoing.',
        ]},
        {
          type: 'callout',
          colour: 'orange',
          text: 'In immediate danger? If you or someone else is at risk right now, call 999. Do not wait.',
        },
      ],
    },
    {
      heading: '7. We are here to help',
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
          after: '  |  Visit www.CoreEd.co.uk  |  The Media Centre, 7 Northumberland Street, Huddersfield, HD1 1RL',
        },
        { type: 'p', text: 'In an emergency, always call 999.', bold: true },
      ],
    },
  ],

  signoff: {
    who: 'The CoreEd Team',
    text: 'Have a good August. We will see you back in the loop next month.',
  },
};
