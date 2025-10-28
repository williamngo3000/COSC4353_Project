import { useState } from 'react';
import { ChevronDownIcon, CheckIcon } from './Icons';

const CustomMultiSelect = ({ options, selected, onChange, placeholder }) => {
    const [isOpen, setIsOpen] = useState(false);

    const toggleOption = (option) => {
        const newSelected = selected.includes(option)
            ? selected.filter(item => item !== option)
            : [...selected, option];
        onChange(newSelected);
    };

    return (
        <div className="multiselect-container">
            <button
                type="button"
                className="multiselect-button"
                onClick={() => setIsOpen(!isOpen)}
            >
                <span className="multiselect-placeholder">
                    {selected.length > 0 ? selected.join(', ') : placeholder}
                </span>
                <span className="multiselect-chevron">
                    <ChevronDownIcon />
                </span>
            </button>
            {isOpen && (
                <div className="multiselect-dropdown">
                    <ul className="multiselect-list">
                        {options.map(option => (
                            <li
                                key={option}
                                className="multiselect-item"
                                onClick={() => toggleOption(option)}
                            >
                                <span className={selected.includes(option) ? 'multiselect-item-text-selected' : ''}>
                                    {option}
                                </span>
                                {selected.includes(option) && (
                                    <span className="multiselect-item-check">
                                        <CheckIcon className="h-5 w-5" />
                                    </span>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default CustomMultiSelect;
