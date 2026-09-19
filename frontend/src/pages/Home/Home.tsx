import { Link } from 'react-router-dom';
import CourseCard from '../../components/CourseCard/CourseCard';
import Skeleton from '../../components/Skeleton/Skeleton';
import { useCourses } from '../../features/courses/useCourses';
import styles from './Home.module.css';

const featureBadges = ['Практика', 'Проекты', 'Сообщество', 'Карьерный рост'];

const features = [
    {
        icon: 'monitor',
        title: 'Актуальные курсы',
        description: 'Современные технологии, понятная теория и реальные задачи для портфолио.',
    },
    {
        icon: 'users',
        title: 'Опытные преподаватели',
        description: 'Практикующие разработчики помогают разобраться в сложных темах без хаоса.',
    },
    {
        icon: 'bolt',
        title: 'Практика с первого дня',
        description: 'Проекты, задания и проверки помогают сразу применять новые навыки.',
    },
    {
        icon: 'chart',
        title: 'Сертификат и карьерный рост',
        description: 'Подтверди знания, отслеживай прогресс и уверенно двигайся в IT.',
    },
];

const Icon = ({ name }: { name: string }) => {
    switch (name) {
        case 'monitor':
            return (
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <rect x="3" y="4" width="18" height="12" rx="2" />
                    <path d="M8 20h8M12 16v4" />
                </svg>
            );
        case 'users':
            return (
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M16 11a4 4 0 1 0-8 0" />
                    <path d="M5 20a7 7 0 0 1 14 0" />
                    <path d="M18 8a3 3 0 0 1 2.6 4.5" />
                    <path d="M20 20a5 5 0 0 0-3-4.5" />
                </svg>
            );
        case 'bolt':
            return (
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="m13 2-8 12h7l-1 8 8-12h-7l1-8Z" />
                </svg>
            );
        case 'chart':
            return (
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M5 19V9" />
                    <path d="M12 19V5" />
                    <path d="M19 19v-7" />
                </svg>
            );
        default:
            return null;
    }
};

const Home = () => {
    const { courses, count, isLoading } = useCourses({ ordering: '-created_at', page: 1 });
    const stats = [
        { value: isLoading ? '...' : String(count), label: 'курсов в каталоге' },
        { value: '4', label: 'уровня сложности' },
        { value: '5', label: 'максимальная оценка', accent: '★' },
        { value: '100%', label: 'онлайн-формат' },
    ];

    return (
        <div className={styles.page}>
            <section className={styles.hero} aria-labelledby="home-hero-title">
                <div className={styles.heroContent}>
                    <p className={styles.eyebrow}>УЧИСЬ • РАЗВИВАЙСЯ • СОЗДАВАЙ БУДУЩЕЕ</p>
                    <h1 id="home-hero-title" className={styles.title}>
                        Изучи программирование и открой{' '}
                        <span className={styles.highlight}>новые возможности</span>
                    </h1>
                    <p className={styles.description}>
                        Практические онлайн-курсы, опытные преподаватели и реальные проекты.
                        Начни путь в IT уже сегодня!
                    </p>

                    <div className={styles.actions}>
                        <Link className={styles.primaryButton} to="/courses">
                            Выбрать курс <span aria-hidden="true">→</span>
                        </Link>
                        <a className={styles.secondaryButton} href="#features">
                            Как это работает?
                        </a>
                    </div>

                    <dl className={styles.stats} aria-label="Статистика платформы">
                        {stats.map((item) => (
                            <div className={styles.statItem} key={item.label}>
                                <dt>
                                    {item.value}
                                    {item.accent && <span className={styles.star}>{item.accent}</span>}
                                </dt>
                                <dd>{item.label}</dd>
                            </div>
                        ))}
                    </dl>
                </div>

                <div className={styles.heroVisual} role="img" aria-label="Студент изучает программирование онлайн">
                    <div className={styles.visualCard}>
                        <div className={styles.studentScene}>
                            <div className={styles.windowDecor} />
                            <div className={styles.person}>
                                <div className={styles.hair} />
                                <div className={styles.face} />
                                <div className={styles.body} />
                            </div>
                            <div className={styles.laptop}>
                                <span>Лучше код</span>
                                <span>ярче будущее</span>
                            </div>
                            <div className={styles.bookStack}>
                                <span>Python</span>
                                <span>React</span>
                                <span>Django</span>
                            </div>
                        </div>

                        <div className={styles.codeCard} aria-hidden="true">
                            <span>function learn() {'{'}</span>
                            <span>  return {'{'}</span>
                            <span>    skills: ['HTML', 'CSS', 'JS'],</span>
                            <span>    mindset: 'growth',</span>
                            <span>  {'}'}</span>
                            <span>{'}'}</span>
                        </div>

                        <div className={styles.badges} aria-hidden="true">
                            {featureBadges.map((badge) => (
                                <span key={badge}>{badge}</span>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            <section id="features" className={styles.features} aria-labelledby="features-title">
                <div className={styles.sectionHeader}>
                    <p className={styles.sectionEyebrow}>Почему выбирают нас</p>
                    <h2 id="features-title">Платформа, где обучение превращается в результат</h2>
                </div>

                <div className={styles.featureGrid}>
                    {features.map((feature) => (
                        <article className={styles.featureCard} key={feature.title}>
                            <div className={styles.featureIcon}>
                                <Icon name={feature.icon} />
                            </div>
                            <h3>{feature.title}</h3>
                            <p>{feature.description}</p>
                        </article>
                    ))}
                </div>
            </section>

            <section className={styles.coursesSection} aria-labelledby="new-courses-title">
                <div className={styles.coursesHeader}>
                    <div>
                        <p className={styles.sectionEyebrow}>Начните обучение</p>
                        <h2 id="new-courses-title">Новые курсы</h2>
                    </div>
                    <Link to="/courses" className={styles.catalogLink}>Смотреть все курсы →</Link>
                </div>

                <div className={styles.courseGrid}>
                    {isLoading
                        ? <Skeleton count={3} />
                        : courses.slice(0, 3).map((course) => <CourseCard key={course.id} course={course} />)}
                </div>

                {!isLoading && courses.length === 0 && (
                    <p className={styles.noCourses}>Опубликованные курсы скоро появятся.</p>
                )}
            </section>
        </div>
    );
};

export default Home;
