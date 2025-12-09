// const app = document.getElementById('app');
// // const header = document.createElement('header');
// // const text = 'Welcome to Toy Project 01';
// // const headerContent = document.createTextNode(text);
// // header.appendChild(headerContent);
// // app.appendChild(header);
// const root = ReactDOM.createRoot(app);
// function Header() {
//   return <h1>Hello, World!</h1>;
// }
// function HomePage() {
//     return (
//         <div>
//             <Header />
//         </div>
//     );
// }
// root.render(<HomePage />);

import LikeButton from './like-button';
 
function Header({ title }) {
  return <h1>{title ? title : 'Default title'}</h1>;
}
 
export default function HomePage() {
  const names = ['Ada Lovelace', 'Grace Hopper', 'Margaret Hamilton'];
 
  return (
    <div>
      <Header title="Develop. Preview. Ship." />
      <ul>
        {names.map((name) => (
          <li key={name}>{name}</li>
        ))}
      </ul>
      <LikeButton />
    </div>
  );
}