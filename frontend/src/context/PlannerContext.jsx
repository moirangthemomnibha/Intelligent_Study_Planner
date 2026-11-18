import {
  createContext,
  useContext,
  useState,
  useMemo,
} from "react";

const PlannerContext = createContext(null);

export function PlannerProvider({ children }) {
  const [subjects, setSubjects] = useState([]);
  const [topics, setTopics] = useState([]);
  const [plan, setPlan] = useState([]);

  // Calculate total topics
  const totalTopics = topics.length;

  // Calculate completed topics
  const completedTopics = topics.filter(
    topic => Number(topic.completion_percent) >= 100
  ).length;

  // Calculate overall syllabus progress
  const overallProgress = useMemo(() => {
    if (totalTopics === 0) return 0;

    const totalCompletion = topics.reduce(
      (sum, topic) =>
        sum + Number(topic.completion_percent || 0),
      0
    );

    return Math.round(totalCompletion / totalTopics);
  }, [topics, totalTopics]);

  // Calculate in-progress topics
  const inProgressTopics = topics.filter(
    topic =>
      Number(topic.completion_percent) > 0 &&
      Number(topic.completion_percent) < 100
  ).length;

  // Calculate not-started topics
  const notStartedTopics = topics.filter(
    topic => Number(topic.completion_percent) === 0
  ).length;

  return (
    <PlannerContext.Provider
      value={{
        subjects,
        setSubjects,

        topics,
        setTopics,

        plan,
        setPlan,

        totalTopics,
        completedTopics,
        overallProgress,
        inProgressTopics,
        notStartedTopics,
      }}
    >
      {children}
    </PlannerContext.Provider>
  );
}

export const usePlanner = () => useContext(PlannerContext);