/**
 * Accessible Word version of In The Loop, August 2026 (learner edition).
 * Wording is kept identical to work/issue.html — the two files are emailed
 * together and read as one thing. build_docx.js turns this into real heading
 * styles, alt text and live links. The QR code in the PDF is replaced here by
 * the survey web address as a live link, since a screen reader cannot scan a QR.
 */
module.exports = {
  title: 'In The Loop',
  issue: 'CoreEd Learner Newsletter  |  Issue: August 2026',
  strapline: 'A monthly update for CoreEd learners.',
  description: 'Accessible version of the In The Loop learner newsletter, August 2026.',

  sections: [
    {
      heading: 'Welcome',
      blocks: [
        { type: 'p', text: 'Welcome to the August issue. It’s the heart of summer. This month we’re talking about your voice and how to use it, looking after wellbeing, including a topic we don’t discuss enough, and the different ways brains work.' },
        { type: 'p', text: 'Whoever you are and wherever you’ve come from, you belong here at CoreEd.' },
        { type: 'p', text: 'Some tutors may be away over the summer, but the team is still here. Corrie, Ben, Priya and the Safety Guardian will point you to the useful bits.' },
        {
          type: 'image', file: 'characters/Mascot_Welcome.png', width: 90, height: 68,
          name: 'CoreEd Safety Guardian mascot',
          description: 'Illustration of the CoreEd Safety Guardian, a friendly shield-shaped mascot, waving hello.',
          caption: 'Illustration: the CoreEd Safety Guardian, waving hello.',
        },
        { type: 'h2', text: 'In this issue' },
        { type: 'bullets', items: [
          '01 — In Their Words',
          '02 — Your Voice, Your Say',
          '03 — Looking After You This Summer',
          '04 — How Brains Work Differently',
          '05 — Your Next Step',
          '06 — Safeguarding Team Update',
          '07 — Looking Out for One Another',
          '08 — Support & Resources',
        ]},
      ],
    },
    {
      heading: '01. In Their Words',
      blocks: [
        { type: 'p', text: 'A learner’s feedback this month.' },
        { type: 'p', text: 'A lovely note from a learner this month, after a session that helped them get back on track:' },
        { type: 'callout', colour: 'blue', text: [
          '“Thank you Sharon — found today’s session really great, and appreciate your support with getting me back on track. Feeling very motivated again!”',
          '— A CoreEd learner',
        ]},
        { type: 'p', text: 'Thank you for sharing, and well done Sharon. If a session helps, or does not, tell your tutor. It is how we make the next one even better.' },
        {
          type: 'image', file: 'characters/Priya_Listening.png', width: 60, height: 108,
          name: 'Priya Shah, assessor',
          description: 'Illustration of Priya Shah, a CoreEd assessor, listening attentively.',
          caption: 'Illustration: Priya Shah, one of our assessors.',
        },
      ],
    },
    {
      heading: '02. Your Voice, Your Say',
      blocks: [
        { type: 'p', text: 'Speaking up, and the survey that shapes CoreEd.' },
        { type: 'p', text: '12 August is International Youth Day, a good reminder that your generation’s voice matters. Advocacy just means speaking up, for yourself and for others. At CoreEd, the simplest way to do that is the learner survey: we read every response, and it shapes what we do next. Not many of you have filled it in yet, so this is your nudge.' },
        { type: 'h2', text: 'Your say, in about two minutes' },
        { type: 'p', text: 'Not sure where to start? Tell us: one thing CoreEd does well, one thing we could do better, and one thing that would make your week easier.' },
        {
          type: 'link',
          before: 'Open the survey here: ',
          text: 'CoreEd learner survey',
          href: 'https://qualityhero.co.uk/f/40e945db4a76a23be6cf0b3dfe2147da7e59c95bb5b46ea9',
          after: '. The QR code in the printed version links to the same address, so you can scan it with your phone camera or ask your tutor to send it over.',
        },
        {
          type: 'image', file: 'characters/Corrie_Happy.png', width: 60, height: 90,
          name: 'Corrie Patel, apprentice',
          description: 'Illustration of Corrie Patel, a CoreEd apprentice, smiling.',
          caption: 'Illustration: Corrie Patel, one of our apprentices.',
        },
      ],
    },
    {
      heading: '03. Looking After You This Summer',
      blocks: [
        { type: 'p', text: 'Including a conversation worth having.' },
        { type: 'p', text: 'Keep the summer basics going: water, sleep, fresh air and a bit of a break. This month we are also putting a plainer light on one topic that carries needless stigma.' },
        { type: 'h2', text: 'Menopause: let’s talk about it' },
        { type: 'p', text: 'Menopause is a natural stage of life, but it’s still something people feel awkward raising. Its effects, on sleep, mood, focus and more, can show up at work and in study. Being understanding, whether it’s you, a colleague or someone at home, makes a real difference. Support is out there: your GP, the NHS, and menopauseinfo.org are good places to start.' },
        { type: 'h2', text: 'Feeling the pressure?' },
        { type: 'callout', colour: 'blue', text: 'Summer can be a real mix, busy for some, quiet for others. Whatever you’re juggling, be kind to yourself and take breaks. If things ever feel heavy, talk to your tutor, and Samaritans (116 123) and Shout (text SHOUT to 85258) are there any time.' },
        {
          type: 'image', file: 'characters/Mascot_Safety_Tip.png', width: 90, height: 69,
          name: 'CoreEd Safety Guardian mascot',
          description: 'Illustration of the CoreEd Safety Guardian sharing a wellbeing tip.',
          caption: 'Illustration: the CoreEd Safety Guardian, sharing a wellbeing tip.',
        },
      ],
    },
    {
      heading: '04. How Brains Work Differently',
      blocks: [
        { type: 'p', text: 'Dyspraxia, dyscalculia and everyday support.' },
        { type: 'p', text: 'This month we’re raising awareness of dyspraxia and dyscalculia, two common ways of learning and thinking. Dyspraxia can affect coordination, organisation and planning; dyscalculia affects working with numbers. Neither has anything to do with how clever you are.' },
        { type: 'h2', text: 'Small adjustments, big difference' },
        { type: 'p', text: 'A bit of extra time, clear step-by-step instructions, checklists, or a different way to show what you know can all help. What works is personal, so there’s no one-size-fits-all.' },
        { type: 'h2', text: 'Tell your tutor' },
        { type: 'p', text: 'If you find some things harder than they feel they should be, you’re not alone, and it’s worth a chat. Ask about reasonable adjustments. The conversation is confidential, and asking is always welcome.' },
        {
          type: 'image', file: 'characters/Priya_Supportive.png', width: 60, height: 92,
          name: 'Priya Shah, assessor',
          description: 'Illustration of Priya Shah, a CoreEd assessor, offering supportive reassurance.',
          caption: 'Illustration: Priya Shah, one of our assessors.',
        },
      ],
    },
    {
      heading: '05. Your Next Step',
      blocks: [
        { type: 'p', text: 'Keep your momentum going.' },
        { type: 'p', text: 'You’re already well into your apprenticeship, so the aim over summer is simple: keep your momentum up. If English or maths Functional Skills are still on your list, your tutor can talk you through what applies to you and plan the next steps together. Whatever stage you’re at, they’re here to help you move forward.' },
        { type: 'h2', text: 'Dates for your diary — August' },
        { type: 'bullets', items: [
          '12 August — International Youth Day.',
          '19 August — World Humanitarian Day.',
          '31 August — Summer Bank Holiday (England & Wales).',
        ]},
        {
          type: 'image', file: 'characters/Ben_Explaining.png', width: 60, height: 97,
          name: 'Ben Carter, mentor',
          description: 'Illustration of Ben Carter, a CoreEd mentor, explaining something with a raised finger.',
          caption: 'Illustration: Ben Carter, one of our mentors.',
        },
      ],
    },
    {
      heading: '06. Safeguarding Team Update',
      blocks: [
        { type: 'p', text: 'Know who to turn to, support is here all summer.' },
        { type: 'p', text: 'Safeguarding is everyone’s responsibility, and the team is reachable over the summer break. Whether it’s about your own wellbeing, someone else’s safety, or a difficult time, please reach out. Speaking up early is always the right thing to do.' },
        { type: 'contact', name: 'Jeannette Adrian', role: 'Designated Safeguarding Lead (DSL) and Wellbeing Support', phone: '07557 093701', email: 'jeannette@CoreEd.co.uk' },
        { type: 'contact', name: 'Airam Neesa', role: 'Deputy Designated Safeguarding Lead', phone: '07912 342 367', email: 'airam@CoreEd.co.uk' },
      ],
    },
    {
      heading: '07. Looking Out for One Another',
      blocks: [
        { type: 'p', text: 'Staying safe, online and off.' },
        { type: 'p', text: 'Summer often means more time online. Part of keeping everyone safe is something called Prevent. Here’s what it means, and who to talk to if something doesn’t feel right.' },
        { type: 'h2', text: 'Support, not suspicion' },
        { type: 'p', text: 'Prevent is part of safeguarding. It’s about helping anyone who might be at risk of being pulled towards extremism or hateful views, the same way we’d help with any other worry. It isn’t about getting anyone into trouble; it’s about getting the right support early.' },
        { type: 'h2', text: 'Think before you share' },
        { type: 'p', text: 'Not everything online is true or safe. If a post, message or account makes you uneasy, or pressures you to do or believe something, step back and talk to someone you trust. Keep your details private and be kind in the group chat.' },
        {
          type: 'link',
          before: 'Worried about something? You can speak to Jeannette or Airam (above), or contact the ACT Early support line on 0800 011 3764 or at ',
          text: 'actearly.uk',
          href: 'https://actearly.uk',
          after: '. In an emergency, always call 999.',
        },
        {
          type: 'image', file: 'characters/Mascot_Warning.png', width: 90, height: 66,
          name: 'CoreEd Safety Guardian mascot',
          description: 'Illustration of the CoreEd Safety Guardian with a hand raised in a gentle stop gesture.',
          caption: 'Illustration: the CoreEd Safety Guardian, with a hand raised.',
        },
      ],
    },
    {
      heading: 'Final thoughts',
      blocks: [
        { type: 'p', text: 'Enjoy the rest of your summer. Keep your momentum going, look after yourselves and each other, and do have your say in the survey too.' },
        { type: 'p', text: '— The CoreEd Team', bold: true },
        {
          type: 'image', file: 'characters/Mascot_Celebration.png', width: 90, height: 61,
          name: 'CoreEd Safety Guardian mascot',
          description: 'Illustration of the CoreEd Safety Guardian celebrating with a thumbs up.',
          caption: 'Illustration: the CoreEd Safety Guardian, celebrating.',
        },
      ],
    },
    {
      heading: '08. Support & Resources',
      blocks: [
        { type: 'h2', text: 'Study & next steps' },
        { type: 'bullets', items: [
          'Your CoreEd tutor — your first port of call for options, Functional Skills and one-to-one help.',
          'National Careers Service — free careers advice and a helpline (nationalcareers.service.gov.uk).',
          'GOV.UK Apprenticeships — how apprenticeships and assessment work (gov.uk).',
        ]},
        { type: 'h2', text: 'Wellbeing & health' },
        { type: 'bullets', items: [
          'NHS, menopause — symptoms, treatments and advice (nhs.uk).',
          'Menopause information — support and stigma-busting resources (menopauseinfo.org).',
          'Samaritans — free, 24/7; call 116 123 in the UK.',
          'Shout — free 24/7 text support; text SHOUT to 85258.',
          'Mind — mental health advice and local services (mind.org.uk).',
        ]},
        { type: 'h2', text: 'Inclusion & learning' },
        { type: 'bullets', items: [
          'Dyspraxia Foundation — information and support (dyspraxiafoundation.org.uk).',
          'British Dyslexia Association — guidance on dyscalculia and more (bdadyslexia.org.uk).',
          'Your CoreEd tutor — to arrange a reasonable adjustment or talk anything through.',
        ]},
      ],
    },
  ],
};
