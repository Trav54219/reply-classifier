"""Ordered regex rules; the first rule that matches decides the label."""
import re

# Order matters: machine and legal-risk labels come before intent labels, and
# "not interested" before "interested" so the negation wins.
RULES = [
    ("left_company", r"no longer (?:with|at|employed|works?|working)|has left (?:the )?(?:company|organi[sz]ation)|have left (?:the )?(?:company|organi[sz]ation)|ceased to be|mailbox is no longer monitored|moved on to a new role|not (?:at|with) (?:this|the|our) (?:company|organi[sz]ation)|(?:employee|colleague) has left|\\bleft [A-Z][\\w&]+"),
    ("out_of_office", r"out of (?:the )?office|out of town|on (?:annual )?leave|auto-?reply|automatic reply|away from (?:my )?(?:desk|email)|currently (?:out|away)|on vacation|maternity|paternity|limited access to (?:email|internet)|\\booo\\b|(?:travell?ing|traveling|away|out) .{0,40}(?:until|through|till)|no access to (?:email|internet)|(?:off|away) until|will (?:reply|respond|get back to you) (?:after|when i)|attending a (?:training|conference|course)|out from "),
    ("unsubscribe", r"unsubscribe|remove me|take me off|stop (?:emailing|contacting|sending|messaging)|do not (?:contact|email)|don'?t (?:contact|email) me|opt.?out|remove (?:me )?from (?:your |this |the )?(?:list|mailing)"),
    ("wrong_person", r"wrong (?:person|contact|email)|not the right (?:person|contact)|i'?m not the (?:right|best)|isn'?t my (?:department|area|role)|not my (?:department|area|role)|i don'?t handle|should (?:reach out|contact|speak|talk) (?:to|with)|(?:try|please) contact(?:ing)? (?:our|the)|forwarded (?:this|your)|wrong guy|wrong team|nothing to do with|you want (?:our|the)|(?:is|this one is) for (?:the|our) .{0,30}(?:team|department)|not me\\b|not really my|pass (?:your|this|the) (?:note|email|message) (?:on )?to"),
    ("not_interested", r"not interested|no,? thank|not (?:a )?(?:fit|priority|looking)|(?:we'?re|we are) (?:all set|good|covered|happy)|already (?:have|work|use|using)|\bpass\b|don'?t need|do not need|in-house|not for us|(?:just )?(?:signed|renewed) (?:a |an )?(?:contract|agreement)|budget (?:is )?(?:frozen|locked)|isn'?t something we|can'?t consider|we handle (?:this|that|it)"),
    ("positive", r"interested|sounds (?:good|great|interesting)|let'?s (?:talk|chat|connect|schedule|set up|do)|happy to (?:chat|talk|connect|hop)|open to (?:a|an|chatting|talking)|send (?:me )?(?:over|some times|a time|times)|calendar|schedule (?:a|something)|\byes\b|works for me|does .{0,25} work\?|(?:up|down) for a|free (?:on )?(?:mon|tues|wednes|thurs|fri)day|learn more on a call|(?:call|reach) me|calendar invite|(?:couple|few) (?:of )?times|love this|timely"),
    ("info_request", r"how much|pricing|\bprice\b|\bcosts?\b|what (?:is|are|do|does|exactly)|tell me more|more (?:info|information|details)|case stud|who are you|how (?:does|do|did)|\?"),
]
COMPILED = [(label, re.compile(pat, re.I)) for label, pat in RULES]

MACHINE = {"out_of_office", "left_company"}
# Labels that mean a person read it and engaged: the numerator for a human reply rate.
HUMAN = {"positive", "info_request", "not_interested", "wrong_person", "unsubscribe", "other"}


def classify(text: str) -> tuple[str, str | None]:
    """Return (label, matched_rule_pattern). Empty or unmatched text is 'other'."""
    for label, rx in COMPILED:
        if rx.search(text or ""):
            return label, rx.pattern[:40]
    return "other", None
