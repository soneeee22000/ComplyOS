"""EU AI Act Ontology Data — Articles 9-15 (high-risk AI system obligations).

This module encodes the legal structure of the EU AI Act as typed Python
dataclasses. The ontology is the source of truth for compliance requirements,
sub-requirements, verification criteria, and cross-references.

Source: Regulation (EU) 2024/1689 (Official Journal, 13 June 2024)
"""

from app.ontology import (
    ApplicableRiskLevel,
    Article,
    CrossReference,
    Ontology,
    SubRequirement,
)

# --- Article 9: Risk Management System ---

ARTICLE_9 = Article(
    id="article_9",
    number=9,
    title="Risk Management System",
    chapter="Chapter III, Section 2",
    summary="High-risk AI systems require a continuous, iterative risk management system established, implemented, documented and maintained throughout the entire lifecycle.",
    applies_to=[ApplicableRiskLevel.HIGH],
    sub_requirements=[
        SubRequirement(
            id="art9_sub1",
            article_id="article_9",
            paragraph="9(1)",
            title="Establish risk management system",
            description="A risk management system shall be established, implemented, documented and maintained. It shall be a continuous iterative process planned and run throughout the entire lifecycle.",
            verification_criteria=[
                "Documented risk management process exists",
                "Process covers entire AI system lifecycle",
                "Process is iterative and updated regularly",
            ],
        ),
        SubRequirement(
            id="art9_sub2a",
            article_id="article_9",
            paragraph="9(2)(a)",
            title="Identify and analyse known risks",
            description="Identification and analysis of the known and reasonably foreseeable risks that the high-risk AI system can pose to health, safety or fundamental rights.",
            verification_criteria=[
                "Risk register with identified risks exists",
                "Risks to health, safety, and fundamental rights covered",
                "Foreseeable misuse scenarios documented",
            ],
            cross_references=[
                CrossReference(
                    target_article="article_72",
                    relationship="delegates_to",
                    description="Post-market monitoring feeds back into risk identification",
                ),
            ],
        ),
        SubRequirement(
            id="art9_sub2b",
            article_id="article_9",
            paragraph="9(2)(b)",
            title="Estimate and evaluate emerging risks",
            description="Estimation and evaluation of risks that may emerge when the system is used in accordance with its intended purpose and under conditions of reasonably foreseeable misuse.",
            verification_criteria=[
                "Risk evaluation methodology defined",
                "Intended purpose scenarios assessed",
                "Misuse scenarios assessed",
            ],
        ),
        SubRequirement(
            id="art9_sub2d",
            article_id="article_9",
            paragraph="9(2)(d)",
            title="Adopt risk management measures",
            description="Adoption of appropriate and targeted risk management measures designed to address identified risks.",
            verification_criteria=[
                "Risk mitigation measures documented for each identified risk",
                "Measures are proportionate to the risk level",
                "Residual risks are documented and accepted",
            ],
        ),
        SubRequirement(
            id="art9_sub5",
            article_id="article_9",
            paragraph="9(5)",
            title="Testing for risk management",
            description="High-risk AI systems shall be tested for the purposes of identifying the most appropriate and targeted risk management measures. Testing shall ensure consistent performance.",
            verification_criteria=[
                "Testing methodology defined",
                "Tests performed prior to market placement",
                "Test results documented with metrics",
            ],
        ),
    ],
    cross_references=[
        CrossReference(
            target_article="article_72",
            relationship="see_also",
            description="Post-market monitoring system complements the risk management system",
        ),
    ],
)

# --- Article 10: Data and Data Governance ---

ARTICLE_10 = Article(
    id="article_10",
    number=10,
    title="Data and Data Governance",
    chapter="Chapter III, Section 2",
    summary="Training, validation and testing data sets shall meet quality criteria and be subject to appropriate data governance and management practices.",
    applies_to=[ApplicableRiskLevel.HIGH],
    sub_requirements=[
        SubRequirement(
            id="art10_sub2a",
            article_id="article_10",
            paragraph="10(2)(a)",
            title="Relevant design choices",
            description="Data governance practices shall concern relevant design choices for data collection and processing.",
            verification_criteria=[
                "Data design decisions documented",
                "Rationale for data choices explained",
            ],
        ),
        SubRequirement(
            id="art10_sub2b",
            article_id="article_10",
            paragraph="10(2)(b)",
            title="Data collection processes",
            description="Data governance shall concern data collection processes and the origin of data, and in the case of personal data, the original purpose of collection.",
            verification_criteria=[
                "Data provenance documented",
                "Collection processes described",
                "Personal data purposes verified against GDPR",
            ],
        ),
        SubRequirement(
            id="art10_sub2f",
            article_id="article_10",
            paragraph="10(2)(f)",
            title="Examination for bias",
            description="Examination in view of possible biases that are likely to affect health and safety or lead to discrimination.",
            verification_criteria=[
                "Bias assessment methodology exists",
                "Bias testing performed on training data",
                "Mitigation measures for identified biases documented",
            ],
        ),
        SubRequirement(
            id="art10_sub3",
            article_id="article_10",
            paragraph="10(3)",
            title="Data set requirements",
            description="Training, validation and testing data sets shall be relevant, sufficiently representative, and to the best extent possible, free of errors and complete in view of the intended purpose.",
            verification_criteria=[
                "Data representativeness assessed",
                "Data quality metrics defined and measured",
                "Data completeness verified for intended use",
            ],
        ),
    ],
    cross_references=[
        CrossReference(
            target_article="article_9",
            relationship="see_also",
            description="Data governance measures must align with risk management findings",
        ),
    ],
)

# --- Article 11: Technical Documentation ---

ARTICLE_11 = Article(
    id="article_11",
    number=11,
    title="Technical Documentation",
    chapter="Chapter III, Section 2",
    summary="Technical documentation shall be drawn up before placing on market, kept up to date, and demonstrate compliance with all requirements in a clear and comprehensive form.",
    applies_to=[ApplicableRiskLevel.HIGH],
    sub_requirements=[
        SubRequirement(
            id="art11_sub1",
            article_id="article_11",
            paragraph="11(1)",
            title="Draw up technical documentation",
            description="Technical documentation shall be drawn up before the system is placed on the market or put into service and shall be kept up to date.",
            verification_criteria=[
                "Technical documentation package exists",
                "Documentation created before market placement",
                "Update process defined and followed",
            ],
        ),
        SubRequirement(
            id="art11_sub1_annex",
            article_id="article_11",
            paragraph="11(1) + Annex IV",
            title="Annex IV content requirements",
            description="Documentation shall contain at minimum the elements set out in Annex IV: general description, development process, monitoring info, risk management, data governance, human oversight, accuracy specs, lifecycle changes.",
            verification_criteria=[
                "General system description included",
                "Development process documented",
                "System architecture described",
                "Monitoring and control measures documented",
                "Risk management system description included",
                "Data governance measures described",
                "Post-market monitoring plan included",
            ],
            cross_references=[
                CrossReference(
                    target_article="article_9",
                    relationship="further_defined_by",
                    description="Risk management section must align with Article 9 requirements",
                ),
            ],
        ),
    ],
    cross_references=[
        CrossReference(
            target_article="article_16",
            relationship="see_also",
            description="Provider obligations include keeping technical documentation (Article 16(d))",
        ),
    ],
)

# --- Article 12: Record-Keeping ---

ARTICLE_12 = Article(
    id="article_12",
    number=12,
    title="Record-Keeping",
    chapter="Chapter III, Section 2",
    summary="High-risk AI systems shall technically allow for automatic recording of events (logs) over the lifetime of the system.",
    applies_to=[ApplicableRiskLevel.HIGH],
    sub_requirements=[
        SubRequirement(
            id="art12_sub1",
            article_id="article_12",
            paragraph="12(1)",
            title="Automatic event logging",
            description="High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system.",
            verification_criteria=[
                "Automatic logging system implemented",
                "Logs cover system lifetime",
                "Log format and storage defined",
            ],
        ),
        SubRequirement(
            id="art12_sub2",
            article_id="article_12",
            paragraph="12(2)",
            title="Traceability of functioning",
            description="Logging capabilities shall ensure a level of traceability of the AI system functioning that is appropriate to the intended purpose.",
            verification_criteria=[
                "Traceability level defined for intended purpose",
                "Input/output logging where appropriate",
                "Decision audit trail maintained",
            ],
        ),
        SubRequirement(
            id="art12_sub3",
            article_id="article_12",
            paragraph="12(3)",
            title="Risk monitoring via logs",
            description="Logging shall enable monitoring of operation with respect to situations that may result in the AI system presenting a risk or a substantial modification.",
            verification_criteria=[
                "Risk-relevant events identified and logged",
                "Anomaly detection on logs exists or is planned",
                "Substantial modification detection mechanism defined",
            ],
        ),
    ],
)

# --- Article 13: Transparency and Information to Deployers ---

ARTICLE_13 = Article(
    id="article_13",
    number=13,
    title="Transparency and Information to Deployers",
    chapter="Chapter III, Section 2",
    summary="High-risk AI systems shall be designed for sufficient operational transparency and accompanied by instructions of use with concise, complete, correct and clear information.",
    applies_to=[ApplicableRiskLevel.HIGH],
    sub_requirements=[
        SubRequirement(
            id="art13_sub1",
            article_id="article_13",
            paragraph="13(1)",
            title="Sufficient operational transparency",
            description="Systems shall be designed and developed to ensure operation is sufficiently transparent to enable deployers to interpret output and use it appropriately.",
            verification_criteria=[
                "System outputs are interpretable",
                "Deployers can understand how outputs are generated",
                "Transparency measures documented",
            ],
        ),
        SubRequirement(
            id="art13_sub2",
            article_id="article_13",
            paragraph="13(2)",
            title="Instructions for use",
            description="Accompanied by instructions of use in appropriate digital format containing concise, complete, correct and clear information relevant and accessible to deployers.",
            verification_criteria=[
                "Instructions for use document exists",
                "Instructions include intended purpose and limitations",
                "Performance characteristics described",
                "Known risks and residual risks documented",
                "Human oversight measures described in instructions",
            ],
        ),
        SubRequirement(
            id="art13_sub3",
            article_id="article_13",
            paragraph="13(3)",
            title="Information content requirements",
            description="Instructions shall include provider identity, system characteristics, performance, limitations, intended purpose, and information on human oversight measures.",
            verification_criteria=[
                "Provider identity and contact info included",
                "System capabilities and limitations clearly stated",
                "Intended and prohibited uses listed",
                "Accuracy metrics and known limitations documented",
            ],
        ),
    ],
)

# --- Article 14: Human Oversight ---

ARTICLE_14 = Article(
    id="article_14",
    number=14,
    title="Human Oversight",
    chapter="Chapter III, Section 2",
    summary="High-risk AI systems shall be designed for effective human oversight during use, including appropriate human-machine interface tools.",
    applies_to=[ApplicableRiskLevel.HIGH],
    sub_requirements=[
        SubRequirement(
            id="art14_sub1",
            article_id="article_14",
            paragraph="14(1)",
            title="Design for human oversight",
            description="Systems shall be designed and developed with appropriate human-machine interface tools that enable effective oversight by natural persons during use.",
            verification_criteria=[
                "Human oversight mechanism exists",
                "Human-machine interface designed for oversight",
                "Oversight covers the period of system use",
            ],
        ),
        SubRequirement(
            id="art14_sub2",
            article_id="article_14",
            paragraph="14(2)",
            title="Prevent or minimise risks",
            description="Human oversight shall aim to prevent or minimise risks to health, safety or fundamental rights under intended purpose and reasonably foreseeable misuse.",
            verification_criteria=[
                "Oversight addresses identified risks",
                "Human can intervene to prevent harmful outcomes",
                "Override mechanism exists for critical decisions",
            ],
        ),
        SubRequirement(
            id="art14_sub4a",
            article_id="article_14",
            paragraph="14(4)(a)",
            title="Understand system capabilities and limitations",
            description="Individuals assigned human oversight shall be able to properly understand the relevant capacities and limitations of the system.",
            verification_criteria=[
                "Training program for oversight personnel exists",
                "Documentation of system capabilities provided to overseers",
                "Limitations clearly communicated",
            ],
        ),
        SubRequirement(
            id="art14_sub4d",
            article_id="article_14",
            paragraph="14(4)(d)",
            title="Ability to decide not to use or disregard output",
            description="Individuals shall be able to decide, in any particular situation, not to use the system or to disregard, override or reverse its output.",
            verification_criteria=[
                "Override mechanism implemented",
                "Human can disregard system output",
                "Decision to not use system is always available",
            ],
        ),
    ],
    cross_references=[
        CrossReference(
            target_article="article_13",
            relationship="see_also",
            description="Transparency requirements support effective human oversight",
        ),
    ],
)

# --- Article 15: Accuracy, Robustness and Cybersecurity ---

ARTICLE_15 = Article(
    id="article_15",
    number=15,
    title="Accuracy, Robustness and Cybersecurity",
    chapter="Chapter III, Section 2",
    summary="High-risk AI systems shall achieve appropriate levels of accuracy, robustness and cybersecurity, and perform consistently throughout their lifecycle.",
    applies_to=[ApplicableRiskLevel.HIGH],
    sub_requirements=[
        SubRequirement(
            id="art15_sub1",
            article_id="article_15",
            paragraph="15(1)",
            title="Appropriate accuracy levels",
            description="Systems shall be designed and developed to achieve an appropriate level of accuracy, and the accuracy levels and metrics shall be declared in instructions of use.",
            verification_criteria=[
                "Accuracy metrics defined and measured",
                "Accuracy levels declared in instructions",
                "Accuracy appropriate for intended purpose",
            ],
        ),
        SubRequirement(
            id="art15_sub2",
            article_id="article_15",
            paragraph="15(2)",
            title="Resilience to errors and inconsistencies",
            description="Systems shall be resilient as regards errors, faults or inconsistencies that may occur within the system or the environment.",
            verification_criteria=[
                "Error handling mechanisms implemented",
                "System tested for fault tolerance",
                "Graceful degradation under adverse conditions",
            ],
        ),
        SubRequirement(
            id="art15_sub3",
            article_id="article_15",
            paragraph="15(3)",
            title="Robustness against manipulation",
            description="Systems shall be resilient against attempts by unauthorised third parties to alter their use, outputs or performance by exploiting vulnerabilities.",
            verification_criteria=[
                "Adversarial robustness testing performed",
                "Vulnerability assessment conducted",
                "Protection against data poisoning and model manipulation",
            ],
        ),
        SubRequirement(
            id="art15_sub4",
            article_id="article_15",
            paragraph="15(4)",
            title="Cybersecurity measures",
            description="Appropriate technical redundancy solutions including backup or fail-safe plans shall address cybersecurity threats.",
            verification_criteria=[
                "Cybersecurity risk assessment performed",
                "Technical redundancy or failsafe plans exist",
                "Security update process defined",
            ],
        ),
    ],
    cross_references=[
        CrossReference(
            target_article="article_9",
            relationship="see_also",
            description="Accuracy and robustness testing feeds into risk management",
        ),
    ],
)


# --- Build the complete ontology ---

EU_AI_ACT_ONTOLOGY = Ontology(
    version="2024.1689.1",
    articles={
        "article_9": ARTICLE_9,
        "article_10": ARTICLE_10,
        "article_11": ARTICLE_11,
        "article_12": ARTICLE_12,
        "article_13": ARTICLE_13,
        "article_14": ARTICLE_14,
        "article_15": ARTICLE_15,
    },
)
